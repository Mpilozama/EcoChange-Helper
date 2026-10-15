import json
import os
import sys
from collections import Counter

import requests
from dotenv import load_dotenv

from utils.stations import haversine_km

load_dotenv()

BASE = "https://api.airqo.net/api/v2"
TIMEOUT = 20

AREAS = {
    "Soweto": (-26.2485, 27.8540),
    "Sandton": (-26.1076, 28.0567),
}


def fetch_grid_summary():
    token = os.environ.get("AIRQO_TOKEN")
    params = {"token": token} if token else {}
    resp = requests.get(f"{BASE}/devices/grids/summary", params=params, timeout=TIMEOUT)
    print("HTTP status:", resp.status_code)
    return resp.json()


def _coords(node):
    lat = node.get("approximate_latitude", node.get("latitude"))
    lon = node.get("approximate_longitude", node.get("longitude"))
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return lat, lon
    return None


def find_sites(node, found):
    """Walk the JSON and collect anything that looks like a site with coordinates.
    Written defensively, because the exact response shape isn't verified yet."""
    if isinstance(node, dict):
        if _coords(node):
            found.append(node)
        for value in node.values():
            find_sites(value, found)
    elif isinstance(node, list):
        for value in node:
            find_sites(value, found)


def main():
    data = fetch_grid_summary()

    if "--raw" in sys.argv:
        print(json.dumps(data, indent=2)[:3000])
        return

    print("Top-level keys:", list(data.keys()) if isinstance(data, dict) else type(data))

    sites, seen = [], set()
    raw = []
    find_sites(data, raw)
    for s in raw:  # remove duplicates
        key = s.get("_id") or s.get("id") or str(_coords(s))
        if key not in seen:
            seen.add(key)
            sites.append(s)

    print("Sites with coordinates:", len(sites))
    countries = Counter(str(s.get("country", "unknown")) for s in sites)
    print("Sites per country:", dict(countries))

    for name, (lat, lon) in AREAS.items():
        rows = []
        for s in sites:
            slat, slon = _coords(s)
            label = s.get("name") or s.get("search_name") or s.get("formatted_name") or "unnamed"
            rows.append((haversine_km(lat, lon, slat, slon), label, s.get("_id") or s.get("id")))
        rows.sort()
        print(f"\nNearest AirQo sites to {name}:")
        for distance, label, site_id in rows[:5]:
            print(f"  {distance:>8} km  {label}  (id: {site_id})")


if __name__ == "__main__":
    main()