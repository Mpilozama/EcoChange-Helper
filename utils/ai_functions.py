import os

import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Put the current model name from Google's docs in .env as GEMINI_MODEL
# so you never have to touch the code when models get retired.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
TIMEOUT = 10  # seconds, so a slow API can't hang the app

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

_client = None


def _get_client():
    """Create the Gemini client on first use, so a missing key doesn't crash on import."""
    global _client
    if _client is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def _ask_gemini(prompt):
    response = _get_client().models.generate_content(model=MODEL, contents=prompt)
    return response.text


def get_climate_data(city):
    """Return city coordinates + PM2.5/ozone, or None if the city isn't found or an API fails."""
    try:
        geo = requests.get(
            GEOCODE_URL, params={"name": city, "count": 1}, timeout=TIMEOUT
        ).json()
        results = geo.get("results")
        if not results:
            return None

        place = results[0]
        lat, lon = place["latitude"], place["longitude"]

        aq = requests.get(
            AIR_URL,
            params={"latitude": lat, "longitude": lon, "current": "pm2_5,ozone"},
            timeout=TIMEOUT,
        ).json()

        return {
            "city": place["name"],
            "lat": lat,
            "lon": lon,
            "pm25": aq["current"]["pm2_5"],
            "ozone": aq["current"]["ozone"],
        }
    except (requests.RequestException, KeyError, ValueError):
        return None


def get_neighbor_data(lat, lon):
    """PLACEHOLDER: a point ~0.1 degree away. Not a real 'wealthy suburb' yet.
    The data engineering phase should replace this with a table of labelled locations."""
    try:
        aq = requests.get(
            AIR_URL,
            params={"latitude": lat + 0.1, "longitude": lon + 0.1, "current": "pm2_5"},
            timeout=TIMEOUT,
        ).json()
        return aq["current"]["pm2_5"]
    except (requests.RequestException, KeyError, ValueError):
        return None


def calculate_footprint(transport, diet, energy):
    transport_map = {"car": 2.3, "electric": 0.8, "public": 0.4, "walking": 0, "bike": 0, "walk": 0}
    diet_map = {"meat_heavy": 3.0, "balanced": 2.0, "vegetarian": 1.5, "vegan": 1.0}
    energy_map = {"fossil": 2.5, "mixed": 1.5, "renewable": 0.5}

    total = (
        transport_map.get(transport, 0)
        + diet_map.get(diet, 0)
        + energy_map.get(energy, 0)
    )
    return round(total, 2)


def get_climate_advice(city_data, score):
    pm25 = city_data["pm25"]
    if pm25 > 15:
        return (
            f"CRITICAL: {city_data['city']}'s air is {round(pm25 / 5, 1)}x over WHO limits. "
            f"Your {score}kg footprint adds to this local crisis."
        )
    return "Your local air is currently stable, but every kg of CO2 matters for 2030."


def get_ai_disruption(user_data, city_data, neighbor_pm25):
    neighbor_line = (
        f"The nearby area has a PM2.5 of {neighbor_pm25}."
        if neighbor_pm25 is not None
        else "Nearby comparison data is unavailable, so skip the neighbor comparison."
    )
    prompt = f"""
    The user lives in {city_data['city']}.
    Their carbon footprint is {user_data['score']}kg today.
    Their local air toxicity (PM2.5) is {city_data['pm25']}.
    {neighbor_line}

    TASK: Write exactly 3 sentences, an 'Uncomfortable Truth'.
    1. Tell them how their specific footprint (from {user_data['transport']}) is trapping heat in their community.
    2. Explain the health damage (lungs, heart, life expectancy).
    3. Highlight the inequality between them and the neighbor (if data is available).
    Tone: Disruptive, haunting, and urgent. No corporate talk. No 'lame' advice.
    """
    try:
        return _ask_gemini(prompt)
    except Exception as e:
        print(f"[gemini error] {e}")
        return (
            f"In {city_data['city']}, PM2.5 sits at {city_data['pm25']} µg/m³. "
            "Fine particles reach deep into the lungs and bloodstream, and the people "
            "breathing the worst air are rarely the ones who chose it."
        )


def get_2030_prediction(city_data, score):
    prompt = f"""
    CONTEXT: It is 2026. The city is {city_data['city']}.
    Current Air Toxicity (PM2.5): {city_data['pm25']} µg/m³.
    User's daily carbon output: {score}kg.

    TASK: Project the reality of this city in the year 2030 if nothing changes.
    Focus on:
    1. The 'Heat Island' effect (how much hotter this specific city will get).
    2. The 'Unbreathable' days per year.
    3. The specific impact on the general public.

    TONE: Brutal, prophetic, and gritty. Max 3 sentences. No fluff.
    """
    try:
        return _ask_gemini(prompt)
    except Exception as e:
        print(f"[gemini error] {e}")
        return (
            f"By 2030, {city_data['city']} faces a 2.5°C surge. "
            "The air will move from 'unhealthy' to 'unbreathable' for 100 days a year."
        )