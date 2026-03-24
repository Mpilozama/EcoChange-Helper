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
@app.route('/calculate', methods=['GET', 'POST']) # Allow BOTH for testing
def calculate():
    print("--- DEBUG: The Calculate Route was Triggered! ---")
    
    if request.method == 'POST':
        # Grab data from form
        user_city = request.form.get('city')
        user_transport = request.form.get('transport')
        
        print(f"--- DEBUG: Received City: {user_city}, Transport: {user_transport} ---")

        # Logic
        score = calculate_footprint({'transport_mode': user_transport, 'distance': 100})
        risk = get_climate_advice(user_city)

        return render_template('footprint.html', 
                               result_score=score, 
                               result_risk=risk, 
                               result_city=user_city)
    
    # If someone accidentally goes to /calculate via GET, send them home
    return "This route requires a form submission. Go back to the home page."

# This starts the server
if __name__ == '__main__':
    app.run(debug=True)