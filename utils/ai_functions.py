import requests
def calculate_footprint(data):

    pass

def get_climate_data(city):
    search_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(search_url).json() #Data
# will add error handling later
    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]
    city_name = geo_response["results"][0]["name"]


    pass


def get_climate_advice(city):

    pass


def classify_impact(score):
    pass


def get_personalized_tips(transport):
    pass
    


def get_2030_prediction(score, city): 
    pass