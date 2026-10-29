import csv
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone

from pipeline import ingest

SNAP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "snapshots")

COLUMNS = [
    "fetched_at", "area_id", "area_name", "lat", "lon", "source", "source_type",
    "metric", "value", "station_name", "station_distance_km", "observed_at",
]


def run():
    # Reuse ingest.py, but point it at a throwaway database
    with tempfile.TemporaryDirectory() as tmp:
        ingest.DB_PATH = os.path.join(tmp, "tmp.db")
        ingest.run()
        with closing(sqlite3.connect(ingest.DB_PATH)) as conn:
            rows = conn.execute(
                f"SELECT {', '.join(COLUMNS)} FROM readings ORDER BY id"
            ).fetchall()

    os.makedirs(SNAP_DIR, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(SNAP_DIR, f"{day}.csv")
    is_new = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(COLUMNS)
        writer.writerows(rows)

    print(f"Appended {len(rows)} rows to {path}")


if __name__ == "__main__":
    run()