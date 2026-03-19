from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    transport = request.form['transport']
    diet = request.form['diet']
    electricity = request.form['electricity']

    return f"""
    <h2>Your Input:</h2>
    <p>Transport: {transport}</p>
    <p>Diet: {diet}</p>
    <p>Electricity: {electricity} kWh</p>
    """

if __name__ == '__main__':
    app.run(debug=True)