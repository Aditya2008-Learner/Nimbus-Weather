from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import requests

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

API_KEY = os.getenv("API_KEY")


# -----------------------------
# Helper Functions
# -----------------------------
def format_time(timestamp, timezone_offset):
    city_timezone = timezone(timedelta(seconds=timezone_offset))
    return datetime.fromtimestamp(
        timestamp,
        tz=city_timezone
    ).strftime("%I:%M %p")


def build_weather(data):
    return {

        "city": data["name"],
        "country": data["sys"]["country"],

        "temperature": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),

        "temp_min": round(data["main"]["temp_min"]),
        "temp_max": round(data["main"]["temp_max"]),

        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],

        "visibility": data["visibility"] // 1000,

        "wind": round(data["wind"]["speed"], 1),

        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "main": data["weather"][0]["main"],

        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],

        "sunrise": format_time(
            data["sys"]["sunrise"],
            data["timezone"]
        ),

        "sunset": format_time(
            data["sys"]["sunset"],
            data["timezone"]
        ),

        "is_day": (
            data["sys"]["sunrise"]
            <= data["dt"]
            <= data["sys"]["sunset"]
        )
    }


def get_aqi(weather):

    aqi_url = (
        "https://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={weather['lat']}"
        f"&lon={weather['lon']}"
        f"&appid={API_KEY}"
    )

    response = requests.get(aqi_url)
    data = response.json()

    weather["aqi"] = data["list"][0]["main"]["aqi"]

    aqi_levels = {

        1: ("Good", "#2ecc71"),
        2: ("Fair", "#f1c40f"),
        3: ("Moderate", "#e67e22"),
        4: ("Poor", "#e74c3c"),
        5: ("Very Poor", "#8e44ad")

    }

    weather["aqi_text"] = aqi_levels[weather["aqi"]][0]
    weather["aqi_color"] = aqi_levels[weather["aqi"]][1]

    return weather


def get_forecast(city):

    forecast_url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(forecast_url)
    data = response.json()

    forecast = []

    for item in data["list"]:

        if "12:00:00" in item["dt_txt"]:

            forecast.append({

                "day": datetime.strptime(
                    item["dt_txt"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%a"),

                "temp": round(item["main"]["temp"]),

                "temp_min": round(item["main"]["temp_min"]),

                "temp_max": round(item["main"]["temp_max"]),

                "humidity": item["main"]["humidity"],

                "pop": int(item["pop"] * 100),

                "description": item["weather"][0]["description"].title(),

                "icon": item["weather"][0]["icon"]

            })

            if len(forecast) == 5:
                break

    return forecast


# -----------------------------
# Home Route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    weather = session.pop("weather", None)
    forecast = session.pop("forecast", [])

    if request.method == "POST":

        city = request.form["city"]

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}"
            f"&appid={API_KEY}"
            "&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:

            weather = build_weather(data)
            weather = get_aqi(weather)

            forecast = get_forecast(city)

        else:

            weather = {

                "error": "City not found."

            }

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast

    )  

# -----------------------------
# Current Location Route
# -----------------------------
@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    current_url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(current_url)
    data = response.json()

    if response.status_code == 200:

        weather = build_weather(data)
        weather = get_aqi(weather)

        forecast = get_forecast(weather["city"])

        session["weather"] = weather
        session["forecast"] = forecast

    else:

        session["weather"] = {
            "error": "Unable to fetch location weather."
        }

        session["forecast"] = []

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)