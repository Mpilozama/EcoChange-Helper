import json
import os

import requests

from utils.ai_functions import GEOCODE_URL, TIMEOUT
from utils.stations import (
    _load_airqo_sites,
    _load_openaq_sites,
    haversine_km,
    is_active,
    measures_pm25,
)

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "za_coverage.json")

CITIES = [
    "Johannesburg", "Pretoria", "Cape Town", "Durban", "Gqeberha",
    "Bloemfontein", "East London", "Polokwane", "Mbombela", "Kimberley",
    "Pietermaritzburg", "Rustenburg", "Mahikeng", "Upington", "George",
]


def geocode_za(name):
    try:
        resp = requests.get(
            GEOCODE_URL, params={"name": name, "count": 10}, timeout=TIMEOUT
        ).json()
    except (requests.RequestException, ValueError):
        return None
    for r in resp.get("results") or []:
        if r.get("country_code") == "ZA":
            return r
    return None


def _nearest(lat, lon, sites):
    best = None
    for s in sites:
        d = haversine_km(lat, lon, s["lat"], s["lon"])
        if best is None or d < best[0]:
            best = (d, s["name"])
    return best or (None, None)


def run():
    airqo = [s for s in _load_airqo_sites() if s.get("country") == "South Africa"]
    openaq = [s for s in _load_openaq_sites() if is_active(s) and measures_pm25(s)]

    report = []
    for name in CITIES:
        place = geocode_za(name)
        if not place:
            print(f"Could not find {name}")
            continue
        lat, lon = place["latitude"], place["longitude"]

        a_km, a_name = _nearest(lat, lon, airqo)
        o_km, o_name = _nearest(lat, lon, openaq)
        options = [(k, n, net) for k, n, net in ((a_km, a_name, "AirQo"), (o_km, o_name, "OpenAQ")) if k is not None]
        best = min(options) if options else (None, None, None)

        report.append({
            "city": name,
            "province": place.get("admin1"),
            "lat": lat,
            "lon": lon,
            "nearest_monitor": best[1],
            "distance_km": best[0],
            "network": best[2],
            "nearest_airqo_km": a_km,
            "nearest_openaq_km": o_km,
        })

    report.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"]))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"{'City':<17}{'Nearest monitor':<38}{'Net':<8}{'km':<7}{'AirQo km':<10}OpenAQ km")
    for r in report:
        print(f"{r['city']:<17}{str(r['nearest_monitor']):<38}{str(r['network']):<8}{str(r['distance_km']):<7}{str(r['nearest_airqo_km']):<10}{r['nearest_openaq_km']}")


if __name__ == "__main__":
    run()