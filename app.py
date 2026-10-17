import json
import os
from datetime import datetime

from flask import Flask, render_template, request

from utils.ai_functions import (
    calculate_footprint,
    get_2030_prediction,
    get_ai_disruption,
    get_area_comparison,
    get_climate_data,
    get_future_scenarios,
    get_neighbor_data,
)
from utils.stations import (
    attach_station_readings,
    get_airqo_for_place,
    get_nearest_station,
    is_active,
    measures_pm25,
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_json(name):
    try:
        with open(os.path.join(BASE_DIR, "data", name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    user_city = (request.form.get("city") or "").strip()
    user_transport = request.form.get("transport")
    user_diet = request.form.get("diet")
    user_energy = request.form.get("energy")
    user_year = request.form.get("year", "2030")

    city_info = get_climate_data(user_city)
    if not city_info:
        return "City not found (or the air quality service is unreachable). Go back and try another location.", 404

    score = calculate_footprint(user_transport, user_diet, user_energy)
    neighbor_pm25 = get_neighbor_data(city_info["lat"], city_info["lon"])
    comparison = attach_station_readings(get_area_comparison(user_city))
    station = get_nearest_station(city_info["lat"], city_info["lon"])
    airqo_place = get_airqo_for_place(city_info["lat"], city_info["lon"])

    scenarios = get_future_scenarios(city_info, score, neighbor_pm25, user_year)

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
        scenarios=scenarios,
        comparison=comparison,
        station=station,
        airqo_place=airqo_place,
        scan_date=datetime.now().strftime("%B %Y"),
    )


@app.route('/coverage')
def coverage():
    report = _load_json("za_coverage.json")
    sites = [
        {"name": s["name"], "lat": s["lat"], "lon": s["lon"]}
        for s in _load_json("airqo_sites.json")
        if s.get("country") == "South Africa"
    ]
    openaq_sites = [
        {"name": s["name"], "lat": s["lat"], "lon": s["lon"], "provider": s.get("provider")}
        for s in _load_json("openaq_sites.json")
        if is_active(s) and measures_pm25(s)
    ]

    # Same distance bands the rest of the app uses
    for r in report:
        d = r.get("distance_km")
        if d is not None and d <= 15:
            r["band"] = "covered"
        elif d is not None and d <= 50:
            r["band"] = "distant"
        else:
            r["band"] = "uncovered"

    uncovered_count = sum(1 for r in report if r["band"] == "uncovered")
    return render_template(
        'coverage.html',
        report=report,
        sites=sites,
        site_count=len(sites),
        openaq_sites=openaq_sites,
        openaq_count=len(openaq_sites),
        uncovered_count=uncovered_count,
    )


if __name__ == "__main__":
    app.run(debug=True)