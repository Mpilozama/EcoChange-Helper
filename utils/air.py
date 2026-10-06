import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Approximate neighbourhood-level coordinates (used by the Compare page)
PLACES = [
    {"name": "Johannesburg CBD", "lat": -26.2041, "lon": 28.0473},
    {"name": "Sandton",          "lat": -26.1076, "lon": 28.0567},
    {"name": "Randburg",         "lat": -26.0936, "lon": 28.0064},
    {"name": "Alexandra",        "lat": -26.1038, "lon": 28.0963},
    {"name": "Soweto",           "lat": -26.2678, "lon": 27.8585},
    {"name": "Orange Farm",      "lat": -26.4667, "lon": 27.8667},
    {"name": "Diepsloot",        "lat": -25.9333, "lon": 28.0167},
    {"name": "Midrand",          "lat": -25.9992, "lon": 28.1263},
    {"name": "Tembisa",          "lat": -25.9964, "lon": 28.2268},
]

# Simplified bands for PM2.5 (µg/m³), loosely based on WHO and US EPA guidance.
# Each advice item is (activity, status, note).
LEVELS = {
    "good": {
        "label": "Good",
        "summary": "Within the WHO daily guideline. Enjoy being outside.",
        "advice": [("Exercise outdoors", "ok", "Go for it."),
                   ("Kids playing outside", "ok", "No limits needed."),
                   ("Open your windows", "ok", "Fresh air is fine."),
                   ("Wear a mask", "ok", "Not needed.")],
    },
    "moderate": {
        "label": "Moderate",
        "summary": "Above the WHO daily guideline. Most people are fine; sensitive people may notice it.",
        "advice": [("Exercise outdoors", "care", "Fine for most. If you have asthma, go lighter."),
                   ("Kids playing outside", "care", "OK, but watch kids with asthma or a cough."),
                   ("Open your windows", "ok", "Fine for now."),
                   ("Wear a mask", "ok", "Not usually needed.")],
    },
    "unhealthy": {
        "label": "Unhealthy",
        "summary": "Well above the guideline. Everyone may feel it, sensitive people most.",
        "advice": [("Exercise outdoors", "avoid", "Move hard workouts indoors or to a cleaner hour."),
                   ("Kids playing outside", "care", "Keep outdoor play short."),
                   ("Open your windows", "avoid", "Keep them closed, especially near busy roads."),
                   ("Wear a mask", "care", "A well-fitted FFP2/N95 helps if you must be out.")],
    },
    "severe": {
        "label": "Very unhealthy",
        "summary": "Far above the guideline. Limit time outside.",
        "advice": [("Exercise outdoors", "avoid", "Stay indoors for exercise."),
                   ("Kids playing outside", "avoid", "Keep them indoors."),
                   ("Open your windows", "avoid", "Keep them closed."),
                   ("Wear a mask", "care", "Wear a well-fitted FFP2/N95 outdoors.")],
    },
}


def classify(pm25):
    """Turn a PM2.5 number into a level key plus its details."""
    if pm25 <= 15:
        key = "good"
    elif pm25 <= 35:
        key = "moderate"
    elif pm25 <= 55:
        key = "unhealthy"
    else:
        key = "severe"
    return key, LEVELS[key]


def find_city(name):
    """City name -> coordinates, or None if not found."""
    r = requests.get(GEO_URL, params={"name": name, "count": 1}, timeout=10)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    c = results[0]
    return {"name": c["name"], "country": c.get("country", ""), "lat": c["latitude"], "lon": c["longitude"]}


def get_air(lat, lon):
    """Current reading plus hourly forecast for one place."""
    r = requests.get(AIR_URL, params={
        "latitude": lat, "longitude": lon,
        "current": "pm2_5", "hourly": "pm2_5",
        "forecast_days": 2, "timezone": "auto",
    }, timeout=10)
    r.raise_for_status()
    return r.json()


def hourly_next_24(data):
    """The next 24 hourly readings, each with its level."""
    now = data["current"]["time"][:13]            # e.g. "2026-10-05T14"
    rows = [(t, v) for t, v in zip(data["hourly"]["time"], data["hourly"]["pm2_5"])
            if t[:13] >= now and v is not None]
    return [{"hour": t[11:13], "value": v, "key": classify(v)[0]} for t, v in rows[:24]]


def best_window(hourly, n=3):
    """Cleanest n-hour stretch in the list."""
    if len(hourly) < n:
        return None
    i = min(range(len(hourly) - n + 1), key=lambda i: sum(b["value"] for b in hourly[i:i + n]))
    chunk = hourly[i:i + n]
    return {"start": chunk[0]["hour"] + ":00", "avg": round(sum(b["value"] for b in chunk) / n, 1)}


def get_air_many(places):
    """Current PM2.5 for many places in ONE request (be kind to the API)."""
    r = requests.get(AIR_URL, params={
        "latitude": ",".join(str(p["lat"]) for p in places),
        "longitude": ",".join(str(p["lon"]) for p in places),
        "current": "pm2_5",
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):        # a single place returns an object, not a list
        data = [data]
    return [{**p, "pm25": d["current"]["pm2_5"]} for p, d in zip(places, data)
            if d["current"]["pm2_5"] is not None]