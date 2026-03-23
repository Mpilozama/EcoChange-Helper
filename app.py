from flask import Flask, render_template, request
from utils.ai_functions import calculate_footprint, get_climate_advice # Connect your logic

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        # 1. Collect all data from the new form
        user_data = {
            "city": request.form.get('city'),
            "kwh": request.form.get('kwh', 0),
            "transport_mode": request.form.get('transport_mode'),
            "distance": request.form.get('distance', 0),
            "diet": request.form.get('diet')
        }
        
        # 2. Use your ai_functions
        total_co2 = calculate_footprint(user_data)
        risk_info = get_climate_advice(user_data["city"])
        
        # 3. Build the result object
        result = {
            "city": user_data["city"],
            "total_co2": total_co2,
            "risk": risk_info,
            "tips": ["Upgrade to LED bulbs", "Reduce meat intake", "Consider carpooling"]
        }
        
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)