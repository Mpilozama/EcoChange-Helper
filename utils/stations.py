import math
import os

import requests
from dotenv import load_dotenv

load_dotenv()

WAQI_URL = "https://api.waqi.info/feed/geo:{lat};{lon}/"
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