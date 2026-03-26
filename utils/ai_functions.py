import requests
def calculate_footprint(data):

    pass

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

    # Dig into the JSON boxes to get the numbers
    pm25 = aq_response["current"]["pm2_5"]
    ozone = aq_response["current"]["ozone"]


    return {
        "city": city_name,
        "lat": lat,
        "lon": lon,
        "pm25": pm25,
        "ozone": ozone
    }




def get_climate_advice(city):

    pass


def classify_impact(score):
    pass


def get_personalized_tips(transport):
    pass
    


def get_2030_prediction(score, city): 
    pass