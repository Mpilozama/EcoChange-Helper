from flask import Flask, render_template, request
from utils.ai_functions import (
    calculate_footprint,
    get_climate_advice,
    get_2030_prediction,
    get_climate_data,
    get_neighbor_data,
    get_ai_disruption

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

    neighbor_pm25 = get_neighbor_data(city_info['lat'], city_info['lon'])

    user_data = {'score': score, 'transport': user_transport}
    city_data = {'city': city_info['city'], 'pm25': city_info['pm25']}
    
    ai_verdict = get_ai_disruption(user_data, city_data, neighbor_pm25)
    prediction_text = get_2030_prediction(city_info, score)

    return render_template(
        'footprint.html',
        result_city=city_info['city'], # Changed 'city' to 'result_city'
        result_score=score,           # Changed 'score' to 'result_score'
        health_text=ai_verdict,       # Changed 'verdict' to 'health_text' (to fill that HTML box)
        prediction_text=prediction_text, 
        pm25=city_info['pm25']        # Matches {{ pm25 }}
    )

if __name__ == '__main__':
    app.run(debug=True)