from flask import Flask, render_template, request
from utils.ai_functions import (
    calculate_footprint,
    get_climate_advice,
    classify_impact,
    get_personalized_tips
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    user_city = request.form.get('city')
    user_transport = request.form.get('transport')

    # Calculate carbon footprint
    score = calculate_footprint({
        'transport_mode': user_transport,
        'distance': 100
    })

    # Get climate risk + tips
    risk = get_climate_advice(user_city)
    tips = get_personalized_tips(user_transport)

    # Classify impact level
    impact_level, impact_message = classify_impact(score)

    return render_template(
        'footprint.html',
        result_city=user_city,
        result_score=score,
        result_risk=risk,
        result_tips=tips,
        impact_level=impact_level,
        impact_message=impact_message
    )

if __name__ == '__main__':
    app.run(debug=True)