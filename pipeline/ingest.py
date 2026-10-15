import os
import sqlite3
from datetime import datetime, timezone

from utils.ai_functions import _get_model_pm25, _load_pairs
from utils.stations import _load_airqo_sites, get_airqo_reading, get_nearest_station

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "readings.db")
INGEST_COUNTRIES = {"South Africa"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,      -- when we collected it (UTC)
    area_id TEXT NOT NULL,         -- which pair from locations.json, or 'airqo-network'
    area_name TEXT NOT NULL,
    lat REAL,
    lon REAL,
    source TEXT NOT NULL,          -- 'open-meteo', 'waqi', or 'airqo'
    source_type TEXT NOT NULL,     -- 'model' or 'measured'
    metric TEXT NOT NULL,          -- 'pm25_ugm3' (model/AirQo) or 'aqi_pm25' (WAQI)
    value REAL,                    -- NULL means we could not get a value
    station_name TEXT,
    station_distance_km REAL,
    observed_at TEXT               -- the monitor's own timestamp, if given
);
"""


def run():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []

    for pair in _load_pairs():
        for area in pair["areas"]:
            base = (now, pair["id"], area["name"], area["lat"], area["lon"])

            # 1. Model estimate (Open-Meteo)
            rows.append(base + (
                "open-meteo", "model", "pm25_ugm3",
                _get_model_pm25(area["lat"], area["lon"]), None, None, None,
            ))

            # 2. Ground measurement (WAQI). A NULL value is kept on purpose:
            #    "no monitor / no reading" is part of the story.
            st = get_nearest_station(area["lat"], area["lon"])
            rows.append(base + (
                "waqi", "measured", "aqi_pm25",
                st["aqi_pm25"] if st else None,
                st["name"] if st else None,
                st["distance_km"] if st else None,
                st["time"] if st else None,
            ))

    # 3. The whole South African AirQo network, not just our paired areas.
    #    area_id is 'airqo-network' so these rows are distinguishable from
    #    the paired-area AirQo rows we might add later.
    for site in _load_airqo_sites():
        if site.get("country") not in INGEST_COUNTRIES:
            continue
        aq = get_airqo_reading(site["id"])
        rows.append((
            now, "airqo-network", site["name"], site["lat"], site["lon"],
            "airqo", "measured", "pm25_ugm3",
            aq["pm25"] if aq else None,
            site["name"], 0.0, aq["time"] if aq else None,
        ))

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(SCHEMA)
        conn.executemany(
            "INSERT INTO readings (fetched_at, area_id, area_name, lat, lon, source, "
            "source_type, metric, value, station_name, station_distance_km, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
    print(f"Saved {len(rows)} readings at {now}")


if __name__ == "__main__":
    run()