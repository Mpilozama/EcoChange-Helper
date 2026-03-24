def calculate_footprint(data):
    """
    Calculates CO2 emissions in kg per month.
    data: dictionary containing 'transport', 'diet', and 'electricity'
    """
    # 1. Electricity (SA Grid is carbon-heavy: ~0.86kg CO2 per kWh)
    # Average home uses about 300-500kWh pm
    elec_co2 = float(data.get('kwh', 0)) * 0.86

    # 2. Transport (kg CO2 per km)
    # Petrol Car: ~0.17kg | Bus: ~0.03kg | Walking: 0kg
    transport_type = data.get('transport_mode', 'walking')
    distance = float(data.get('distance', 0))
    
    factors = { 
        "car": 0.17,
        "bus": 0.03,
        "train": 0.02,
        "walking": 0
    }
    transport_co2 = distance * factors.get(transport_type, 0)

    # 3. Diet (Daily kg CO2 converted to monthly)
    # Meat-heavy: ~3.3kg/day | Vegan: ~1.5kg/day
    diet_type = data.get('diet', 'omnivore')
    diet_factors = {
        "meat_heavy": 3.3 * 30,
        "omnivore": 2.5 * 30,
        "vegetarian": 1.7 * 30,
        "vegan": 1.5 * 30
    }
    diet_co2 = diet_factors.get(diet_type, 75)

    total = elec_co2 + transport_co2 + diet_co2
    return round(total, 2)

def get_climate_advice(city):
    # Quick lookup for local demo
    risks = {
        "johannesburg": "Increasing urban heat islands and flash floods.",
        "cape town": "Severe drought risk and rising sea levels.",
        "durban": "High intensity storms and coastal erosion."
    }
    return risks.get(city.lower(), "General unpredictable weather patterns.")



# utils/ai_functions.py

def get_climate_advice(city, transport_km, diet):
    # Local Risk Data (Simulating AI analysis)
    risks = {
        "johannesburg": "High risk of urban heat islands and flash floods.",
        "cape town": "Severe water scarcity risks and coastal erosion.",
        "durban": "Increasing tropical storm intensity and humidity."
    }
    
    risk_info = risks.get(city.lower(), "General environmental shifts and unpredictable weather patterns.")
    
    # Simple Carbon Logic
    diet_impact = {"vegan": 1.5, "vegetarian": 2.5, "meat": 5.0}.get(diet.lower(), 3.5)
    total_impact = (transport_km * 0.2) + diet_impact
    
    return {
        "risk": risk_info,
        "score": round(total_impact, 2),
        "tips": [
            "Switch to LED bulbs to reduce electricity load.",
            "Consider carpooling for your weekly commute.",
            "Plant indigenous shrubs to support local biodiversity."
        ]
    }