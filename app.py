from datetime import datetime

from flask import Flask, render_template, request

from utils.ai_functions import (
    calculate_footprint,
    get_2030_prediction,
    get_ai_disruption,
    get_climate_data,
    get_neighbor_data,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    user_city = (request.form.get("city") or "").strip()
    user_transport = request.form.get("transport")
    user_diet = request.form.get("diet")
    user_energy = request.form.get("energy")

    city_info = get_climate_data(user_city)
    if not city_info:
        return "City not found (or the air quality service is unreachable). Go back and try another location.", 404

    score = calculate_footprint(user_transport, user_diet, user_energy)
    neighbor_pm25 = get_neighbor_data(city_info["lat"], city_info["lon"])

    user_data = {"score": score, "transport": user_transport}
    city_data = {"city": city_info["city"], "pm25": city_info["pm25"]}

    ai_verdict = get_ai_disruption(user_data, city_data, neighbor_pm25)
    prediction_text = get_2030_prediction(city_info, score)

    return render_template(
        "footprint.html",
        result_city=city_info["city"],
        result_score=score,
        health_text=ai_verdict,
        prediction_text=prediction_text,
        pm25=city_info["pm25"],
        ozone=city_info["ozone"],
        neighbor_pm25=neighbor_pm25 if neighbor_pm25 is not None else "unavailable",
        scan_date=datetime.now().strftime("%B %Y"),
    )


if __name__ == "__main__":
    app.run(debug=True)