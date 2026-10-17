import json
import math
import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

WAQI_URL = "https://api.waqi.info/feed/geo:{lat};{lon}/"
WAQI_BOUNDS_URL = "https://api.waqi.info/map/bounds/"
AIRQO_BASE = "https://api.airqo.net/api/v2"
TIMEOUT = 10

# Distance bands (km) for describing monitoring coverage.
# These cut-offs are our own choice, so adjust them if you like.
NEAR_KM = 5
FAR_KM = 15

# Beyond this distance, a "nearest" station is not measuring the queried area
# in any meaningful sense. The template uses this to suppress misleading readings.
MAX_USEFUL_KM = 50


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two coordinates, in km."""
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 1)


def coverage_label(distance_km):
    if distance_km <= NEAR_KM:
        return "nearby"
    if distance_km <= FAR_KM:
        return "wider area"
    return "none nearby"


def get_nearest_station(lat, lon):
    """Return the nearest ground monitor's latest reading, or None if unavailable.
    WAQI returns an AQI (index), not a concentration in µg/m³."""
    token = os.environ.get("WAQI_TOKEN")
    if not token:
        return None
    try:
        resp = requests.get(
            WAQI_URL.format(lat=lat, lon=lon),
            params={"token": token},
            timeout=TIMEOUT,
        ).json()
        if resp.get("status") != "ok":
            return None

        data = resp["data"]
        st_lat, st_lon = data["city"]["geo"]
        distance = haversine_km(lat, lon, st_lat, st_lon)
        pm25 = (data.get("iaqi", {}).get("pm25") or {}).get("v")

        return {
            "name": data["city"]["name"],
            "distance_km": distance,
            "coverage": coverage_label(distance),
            "aqi_pm25": pm25,
            "time": (data.get("time") or {}).get("iso"),
            "source": "World Air Quality Index Project (WAQI)",
            "source_type": "measured",
        }
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None


def get_stations_nearby(lat, lon, radius_km=15):
    """List ground monitors within radius_km, nearest first.
    Returns None if the lookup failed, and [] if the lookup worked but found none.
    That difference matters: 'no monitors' is a finding, 'lookup failed' is not.
    Note: WAQI's bounds endpoint is not a complete inventory of every monitor
    in a region — [] means 'WAQI's map returned none for this box', not
    'no monitors exist here'. Treat both findings with appropriate caution.
    Each station has a 'status' of 'reporting' or 'offline'; offline monitors
    exist but aren't currently returning a reading, which is a separate finding."""
    token = os.environ.get("WAQI_TOKEN")
    if not token:
        return None

    dlat = radius_km / 111
    dlon = radius_km / (111 * math.cos(math.radians(lat)))
    latlng = f"{lat - dlat},{lon - dlon},{lat + dlat},{lon + dlon}"

    try:
        resp = requests.get(
            WAQI_BOUNDS_URL,
            params={"latlng": latlng, "token": token},
            timeout=TIMEOUT,
        ).json()
        if resp.get("status") != "ok":
            return None

        stations = []
        for s in resp.get("data", []):
            distance = haversine_km(lat, lon, s["lat"], s["lon"])
            if distance > radius_km:
                continue
            info = s.get("station") or {}
            aqi_raw = s.get("aqi")
            if aqi_raw in (None, "-"):
                aqi_value, status = None, "offline"
            else:
                try:
                    aqi_value, status = float(aqi_raw), "reporting"
                except (TypeError, ValueError):
                    aqi_value, status = None, "offline"
            stations.append({
                "name": info.get("name"),
                "distance_km": distance,
                "aqi": aqi_value,
                "status": status,
                "last_update": info.get("time"),
            })
        return sorted(stations, key=lambda x: x["distance_km"])
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None


def attach_station_readings(comparison):
    """Add the nearest ground monitor to each area in a paired comparison.
    Flags when both areas are served by the same monitor."""
    if not comparison:
        return comparison
    for area in comparison["areas"]:
        area["station"] = get_nearest_station(area["lat"], area["lon"])
    stations = [a["station"] for a in comparison["areas"]]
    comparison["same_station"] = (
        None not in stations and stations[0]["name"] == stations[1]["name"]
    )
    return comparison


def _airqo_number(field):
    """AirQo may return pm2_5 as a plain number or as an object with a 'value'."""
    if isinstance(field, dict):
        field = field.get("value", field.get("calibratedValue"))
    return float(field) if isinstance(field, (int, float)) else None


def get_airqo_reading(site_id, debug=False):
    """Latest PM2.5 (µg/m³) from an AirQo monitoring site, or None if unavailable.
    Set debug=True to print the raw response, useful the first time.
    Returns None if AIRQO_TOKEN is not set — this endpoint requires auth."""
    token = os.environ.get("AIRQO_TOKEN")
    if not token or not site_id:
        return None
    try:
        resp = requests.get(
            f"{AIRQO_BASE}/devices/measurements/sites/{site_id}/recent",
            params={"token": token},
            timeout=TIMEOUT,
        )
        data = resp.json()
        if debug:
            print("HTTP", resp.status_code)
            print(json.dumps(data, indent=2)[:2500])
        if not data.get("success"):
            return None
        measurements = data.get("measurements") or []
        if not measurements:
            return None

        latest = max(measurements, key=lambda m: m.get("time") or "")
        return {
            "pm25": _airqo_number(latest.get("pm2_5")),
            "time": latest.get("time"),
            "hours_old": latest.get("timeDifferenceHours"),
            "category": latest.get("aqi_category"),
            "source": "AirQo",
            "source_type": "measured",
        }
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        return None


SITES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "airqo_sites.json")
AIRQO_MAX_KM = 50  # beyond this, a monitor says nothing about the place


def _load_airqo_sites():
    try:
        with open(SITES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def get_nearest_airqo_site(lat, lon):
    best = None
    for s in _load_airqo_sites():
        d = haversine_km(lat, lon, s["lat"], s["lon"])
        if best is None or d < best["distance_km"]:
            best = {**s, "distance_km": d}
    return best


def get_airqo_for_place(lat, lon):
    """For ANY coordinates: nearest AirQo monitor, how far, and its latest reading."""
    site = get_nearest_airqo_site(lat, lon)
    if not site:
        return None
    within = site["distance_km"] <= AIRQO_MAX_KM
    return {
        "site": site,
        "within_range": within,
        "coverage": coverage_label(site["distance_km"]),
        "reading": get_airqo_reading(site["id"]) if within else None,
    }


OPENAQ_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "openaq_sites.json")
ACTIVE_DAYS = 30


def _load_openaq_sites():
    try:
        with open(OPENAQ_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def is_active(site, days=ACTIVE_DAYS):
    """True if the monitor reported data within the last `days` days."""
    last = site.get("last_utc")
    if not last:
        return False
    try:
        when = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return False
    return when >= datetime.now(timezone.utc) - timedelta(days=days)


def measures_pm25(site):
    return "pm25" in (site.get("parameters") or [])