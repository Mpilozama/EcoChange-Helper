def calculate_footprint(data):
    transport_type = data.get('transport_mode', 'walking')
    distance = float(data.get('distance', 0))

    factors = {
        "car": 0.17,
        "bus": 0.03,
        "walking": 0
    }

    transport_co2 = distance * factors.get(transport_type, 0)

    # Assume average diet & electricity for MVP
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