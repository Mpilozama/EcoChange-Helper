import requests

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

def get_2030_prediction(score, city):
 
    if score > 5:
        return f"By 2030, this lifestyle in {city} could contribute to a 2°C local heat increase, hitting lower-income areas hardest."