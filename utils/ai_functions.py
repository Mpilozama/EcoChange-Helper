import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY" ))
model = genai.Model('gemini-1.5-flash')

def get_neighbor_data(lat, lon):

    neighbor_lat = lat + 0.1
    neighbor_lon = lon + 0.1
    
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={neighbor_lat}&longitude={neighbor_lon}&current=pm2_5"
    response = requests.get(url).json()
    return response['current']['pm2_5']

def get_ai_disruption(user_data, city_data, neighbor_pm25):
   
    
    prompt = f"""
    The user lives in {city_data['city']}. 
    Their carbon footprint is {user_data['score']}kg today.
    Their local air toxicity (PM2.5) is {city_data['pm25']}.
    The nearby wealthy suburb has a PM2.5 of {neighbor_pm25}.
    
    TASK: Write a 3-sentence 'Uncomfortable Truth'. 
    1. Tell them how their specific footprint (from {user_data['transport']}) is trapping heat in their community.
    2. Explain the health damage (not just mental—think lungs, heart, life expectancy).
    3. Highlight the inequality between them and the neighbor.
    Tone: Disruptive, emotional, and urgent. No corporate talk.
    TONE: Disruptive, haunting, and urgent. Max 4 sentences. No 'lame' advice.
    """
    response = model.generate_content(prompt)
    return response.text


def calculate_footprint(transport, diet, energy):
    transport_map = {"car": 2.3, "electric": 0.8, "public": 0.4, "bike": 0, "walk": 0}
    diet_map = {"meat_heavy": 3.0, "balanced": 2.0, "vegetarian": 1.5, "vegan": 1.0}
    energy_map = {"fossil": 2.5, "mixed": 1.5, "renewable": 0.5}

    total = (transport_map.get(transport, 0) + 
                   diet_map.get(diet, 0) + 
                   energy_map.get(energy, 0))
    
    return round(total, 2)

def get_climate_data(city):
    search_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(search_url).json() #Data
# will add error handling later

#CO-ordinates:
    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]
    city_name = geo_response["results"][0]["name"]

    # Air Qualuty data
    aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5,ozone"
    aq_response = requests.get(aq_url).json()

    pm25 = aq_response["current"]["pm2_5"]
    ozone = aq_response["current"]["ozone"]

    return {
        "city": city_name,
        "lat": lat,
        "lon": lon,
        "pm25": pm25,
        "ozone": ozone
    }

def get_climate_advice(city_data, score):
    # Health Damage Logic
    pm25 = city_data['pm25']
    if pm25 > 15:
        return f"CRITICAL: {city_data['city']}'s air is {round(pm25/5, 1)}x over WHO limits. Your {score}kg footprint adds to this local crisis."
    return "Your local air is currently stable, but every kg of CO2 matters for 2030."

def get_2030_prediction(city_data, score):
    # Using the same Gemini model you configured at the top of the file
    
    prompt = f"""
    CONTEXT: It is 2026. The city is {city_data['city']}. 
    Current Air Toxicity (PM2.5): {city_data['pm25']}µg/m³.
    User's daily carbon output: {score}kg.
    
    TASK: Project the reality of this city in the year 2030 if nothing changes.
    Focus on: 
    1. The 'Heat Island' effect (how much hotter this specific city will get).
    2. The 'Unbreathable' days per year.
    3. The specific impact on the general public (not just students).
    
    TONE: Brutal, prophetic, and gritty. Max 3 sentences. No fluff.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        # Backup if AI fails during the demo
        return f"By 2030, {city_data['city']} faces a 2.5°C surge. The air will move from 'unhealthy' to 'unbreathable' for 100 days a year."