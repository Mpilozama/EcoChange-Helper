import json
import os

import requests

from utils.ai_functions import GEOCODE_URL, TIMEOUT
from utils.stations import _load_airqo_sites, haversine_km

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


def run():
    sites = [s for s in _load_airqo_sites() if s.get("country") == "South Africa"]
    report = []
    for name in CITIES:
        place = geocode_za(name)
        if not place:
            print(f"Could not find {name}")
            continue
        nearest = min(
            ((haversine_km(place["latitude"], place["longitude"], s["lat"], s["lon"]), s["name"]) for s in sites),
            default=(None, None),
        )
        report.append({
            "city": name,
            "province": place.get("admin1"),
            "lat": place["latitude"],
            "lon": place["longitude"],
            "nearest_monitor": nearest[1],
            "distance_km": nearest[0],
        })

    report.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"]))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"{'City':<18}{'Province':<20}{'Nearest AirQo monitor':<40}km")
    for r in report:
        print(f"{r['city']:<18}{str(r['province']):<20}{str(r['nearest_monitor']):<40}{r['distance_km']}")


if __name__ == "__main__":
    run()