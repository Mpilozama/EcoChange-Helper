import requests



def calculate_footprint(data):
    transport_type = data.get('transport_mode', 'walking')
    distance = float(data.get('distance', 0))

    factors = {
        "car": 0.17,
        "bus": 0.03,
        "walking": 0
    }

    transport_co2 = distance * factors.get(transport_type, 0)

  
    diet_co2 = 75
    electricity_co2 = 200

    total = transport_co2 + diet_co2 + electricity_co2
    return round(total, 2)


def get_climate_advice(city):
    risks = {
        "johannesburg": "High risk of urban heat islands and flash floods.",
        "cape town": "Severe drought risk and rising sea levels.",
        "durban": "Increasing tropical storms and coastal erosion."
    }

    return risks.get(city.lower(), "General climate variability and unpredictable weather patterns.")


def classify_impact(score):
    if score < 150:
        return "low", "Your carbon footprint is below the global monthly average."
    elif score < 250:
        return "moderate", "Your emissions are close to the global average."
    else:
        return "high", "Your emissions are significantly above sustainable levels."


def get_personalized_tips(transport):
    if transport == "car":
        return [
            "Try using public transport twice a week to cut emissions.",
            "Carpooling can reduce your transport footprint by up to 40%.",
            "Combine multiple errands into one trip to save fuel."
        ]
    elif transport == "bus":
        return [
            "Public transport already lowers your footprint—great choice.",
            "Walking short distances instead of taking the bus further reduces emissions.",
            "Support green transport initiatives in your community."
        ]
    else:
        return [
            "Walking or cycling produces zero transport emissions—excellent choice.",
            "Encourage others to adopt sustainable transport methods.",
            "Support local infrastructure that promotes safe cycling."
        ]
    
def get_real_climate_data(city):

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    
    try:
        geo_res = requests.get(geo_url).json()
        if not geo_res.get('results'):
            return "Data Unavailable", "We couldn't locate this specific region's climate sensors."
        
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']

        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5"
        aq_res = requests.get(aq_url).json()
        
        aqi = aq_res['current']['us_aqi']
        

        if aqi > 100:
            risk = "Poor Air Quality detected."
            insight = "This region shows high particulate matter, often linked to industrial inequality (SDG 10)."
        else:
            risk = "Stable Air Quality."
            insight = "Current levels are sustainable, but urban growth by 2030 requires proactive greening."
            
        return risk, insight

    except Exception as e:
        return "Connection Error", "The AI is currently unable to reach local climate sensors."