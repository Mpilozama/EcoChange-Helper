import requests
from flask import Flask, render_template, request
from utils.air import (find_city, get_air, get_air_many, classify,
                       hourly_next_24, best_window, PLACES)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    name = request.form.get("city", "").strip()
    if not name:
        return render_template("index.html", error="Please type a city or town.")
    try:
        city = find_city(name)
        if city is None:
            return render_template("index.html",
                error=f"We couldn't find “{name}”. Check the spelling or try a larger nearby town.")
        data = get_air(city["lat"], city["lon"])
    except requests.RequestException:
        return render_template("index.html",
            error="We couldn't reach the air quality service. Please try again in a moment.")

    pm25 = data["current"]["pm2_5"]
    if pm25 is None:
        return render_template("index.html", error="No air data is available for that place right now.")

    key, level = classify(pm25)
    hourly = hourly_next_24(data)
    return render_template("result.html", city=city, pm25=pm25, key=key,
                           level=level, hourly=hourly, best=best_window(hourly))


@app.route("/compare")
def compare():
    try:
        areas = get_air_many(PLACES)
    except requests.RequestException:
        return render_template("compare.html", areas=[],
            error="We couldn't reach the air quality service. Please try again in a moment.")
    for a in areas:
        a["key"] = classify(a["pm25"])[0]
    areas.sort(key=lambda a: a["pm25"], reverse=True)   # worst first
    return render_template("compare.html", areas=areas)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)