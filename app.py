# Import the Flask library to create a web server
from flask import Flask, render_template, request
# Import your custom logic from the utils folder
from utils.ai_functions import calculate_footprint, get_climate_advice

# Initialize the Flask application
app = Flask(__name__)

# DOCTRINE: The "@app.route" tells Flask which URL should trigger this function.
# '/' is the homepage (root).
@app.route('/')
def index():
    # render_template looks inside the 'templates' folder for the HTML file
    return render_template('index.html')

# This route handles the FORM data sent from the website
@app.route('/calculate', methods=['POST'])
def calculate():
    # 1. 'request.form.get' pulls data from the HTML input 'name' attributes
    user_city = request.form.get('city')
    user_transport = request.form.get('transport')
    
    # 2. We pass that data into your logic functions
    # (Assume 100km distance for now for the demo)
    score = calculate_footprint({'transport_mode': user_transport, 'distance': 100})
    risk = get_climate_advice(user_city)

    # 3. We send the results back to 'footprint.html'
    # We give the HTML variables: result_score, result_risk, and result_city
    return render_template('footprint.html', 
                           result_score=score, 
                           result_risk=risk, 
                           result_city=user_city)

# This starts the server
if __name__ == '__main__':
    app.run(debug=True)