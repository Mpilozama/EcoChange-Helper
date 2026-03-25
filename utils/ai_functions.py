def calculate_footprint(data):
    elec_co2 = float(data.get('kwh', 0)) * 0.86

    transport_type = data.get('transport_mode', 'walking')
    distance = float(data.get('distance', 0))

    factors = { 
        "car": 0.17,
        "bus": 0.03,
        "walking": 0
    }

    transport_co2 = distance * factors.get(transport_type, 0)

    diet_type = data.get('diet', 'omnivore')
    diet_factors = {
        "omnivore": 2.5 * 30,
        "vegetarian": 1.7 * 30,
        "vegan": 1.5 * 30
    }

    diet_co2 = diet_factors.get(diet_type, 75)

    total = elec_co2 + transport_co2 + diet_co2
    return round(total, 2)


def get_climate_advice(city):
    risks = {
        "johannesburg": "High risk of urban heat islands and flash floods.",
        "cape town": "Severe water scarcity risks and coastal erosion.",
        "durban": "Increasing tropical storm intensity and humidity."
    }

    tips = [
        "Switch to LED bulbs to reduce electricity usage.",
        "Use public transport or carpool when possible.",
        "Support local tree planting initiatives."
    ]

    return risks.get(city.lower(), "General environmental shifts and unpredictable weather patterns."), tips