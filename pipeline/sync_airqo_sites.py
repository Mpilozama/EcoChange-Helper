import json
import os

from pipeline.airqo_explore import _coords, fetch_grid_summary, find_sites

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "airqo_sites.json")


def run():
    data = fetch_grid_summary()
    raw, sites, seen = [], [], set()
    find_sites(data, raw)

    for s in raw:
        site_id = s.get("_id") or s.get("id")
        if not site_id or site_id in seen:
            continue
        seen.add(site_id)
        lat, lon = _coords(s)
        sites.append({
            "id": site_id,
            "name": s.get("name") or s.get("search_name") or s.get("formatted_name") or "unnamed",
            "country": s.get("country"),
            "city": s.get("city"),
            "region": s.get("region") or s.get("province"),
            "lat": lat,
            "lon": lon,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2)

    print(f"Saved {len(sites)} sites to {OUT}")
    za = [s for s in sites if s["country"] == "South Africa"]
    print(f"\nSouth African sites ({len(za)}):")
    for s in sorted(za, key=lambda x: (str(x["region"]), x["name"])):
        print(f"  {s['name']}  |  city: {s['city']}  region: {s['region']}  ({s['lat']:.3f}, {s['lon']:.3f})")


if __name__ == "__main__":
    run()