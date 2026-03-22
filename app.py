from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        # Get data from the form
        city = request.form.get('city')
        diet = request.form.get('diet') # e.g., "meat", "vegan"
        
        # Simple Logic (Your "AI" Engine)
        if "london" in city.lower():
            risk = "Increased flooding and heatwaves."
        else:
            risk = "General shifts in seasonal rainfall and rising temps."
            
        result = {
            "city": city,
            "risk": risk,
            "tips": ["Use public transport", "Reduce meat intake", "Switch to LED bulbs"]
        }
        
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)