from flask import Flask, render_template, request
from utils.ai_functions import (
    calculate_footprint,
    get_climate_advice,
    get_2030_prediction,
    get_climate_data
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # 1. Get User Input from Form
    user_city = request.form.get('city')
    user_transport = request.form.get('transport')
    user_diet = request.form.get('diet')
    user_energy = request.form.get('energy') # Make sure this is in your HTML!

   
    city_info = get_climate_data(user_city)
    
    if not city_info:
        return "City not found. Please go back and try a real location."

    score = calculate_footprint(user_transport, user_diet, user_energy)

    health_advice = get_climate_advice(city_info, score)
    prediction = get_2030_prediction(score, user_city)

    return render_template(
        'footprint.html',
        result_city=city_info['city'],
        result_score=score,
        health_text=health_advice,
        prediction_text=prediction,
        pm25=city_info['pm25']
    )

if __name__ == '__main__':
    app.run(debug=True)