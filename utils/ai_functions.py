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