import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

OPENAQ_URL = "https://api.openaq.org/v3/locations"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "openaq_sites.json")
TIMEOUT = 30
PAGE_SIZE = 1000


def _utc(field):
    """OpenAQ gives timestamps as {'utc': ..., 'local': ...}."""
    return field.get("utc") if isinstance(field, dict) else field


def normalize(loc):
    coords = loc.get("coordinates") or {}
    lat, lon = coords.get("latitude"), coords.get("longitude")
    if lat is None or lon is None:
        return None
    params = sorted({
        (s.get("parameter") or {}).get("name")
        for s in loc.get("sensors", [])
        if (s.get("parameter") or {}).get("name")
    })
    return {
        "id": loc.get("id"),
        "name": loc.get("name") or "unnamed",
        "locality": loc.get("locality"),
        "provider": (loc.get("provider") or {}).get("name"),
        "is_monitor": loc.get("isMonitor"),   # True = reference-grade monitor
        "lat": lat,
        "lon": lon,
        "parameters": params,
        "last_utc": _utc(loc.get("datetimeLast")),
    }


def run():
    key = os.environ.get("OPENAQ_API_KEY")
    if not key:
        print("Set OPENAQ_API_KEY in your .env first.")
        return

    sites, page = [], 1
    while True:
        resp = requests.get(
            OPENAQ_URL,
            params={"iso": "ZA", "limit": PAGE_SIZE, "page": page},
            headers={"X-API-Key": key},
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            print("HTTP", resp.status_code, resp.text[:300])
            break
        results = resp.json().get("results", [])
        if page == 1 and "--raw" in sys.argv and results:
            print(json.dumps(results[0], indent=2)[:2500])
        for loc in results:
            s = normalize(loc)
            if s:
                sites.append(s)
        if len(results) < PAGE_SIZE:
            break
        page += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2)

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    def recent(s):
        try:
            return datetime.fromisoformat(s["last_utc"].replace("Z", "+00:00")) >= cutoff
        except (AttributeError, ValueError, TypeError):
            return False

    pm25 = [s for s in sites if "pm25" in s["parameters"]]
    print(f"Saved {len(sites)} South African OpenAQ locations")
    print("By provider:", dict(Counter(str(s["provider"]) for s in sites)))
    print("Reference-grade monitors:", sum(1 for s in sites if s["is_monitor"]))
    print("Measure PM2.5:", len(pm25))
    print("Reported in the last 30 days:", sum(1 for s in sites if recent(s)))
    print("Active AND measure PM2.5:", sum(1 for s in pm25 if recent(s)))


if __name__ == "__main__":
    run()