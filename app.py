# -----------------------------
# Home Route
# -----------------------------

from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import requests
import os

# ==========================================
# Configuration
# ==========================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

API_KEY = os.getenv("API_KEY")


# ==========================================
# Helper Functions
# ==========================================

def format_time(timestamp, timezone_offset):
    city_timezone = timezone(timedelta(seconds=timezone_offset))

    return datetime.fromtimestamp(
        timestamp,
        tz=city_timezone
    ).strftime("%I:%M %p")


def build_weather(data):

    weather = {

        "city": data["name"],
        "country": data["sys"]["country"],

        "temperature": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),
        "temp_min": round(data["main"]["temp_min"]),
        "temp_max": round(data["main"]["temp_max"]),

        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "visibility": data["visibility"] // 1000,
        "clouds": data["clouds"]["all"],

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
        ),

        "tip": "",
        "rain_chance": 0,
        "aqi": 0,
        "aqi_text": "",
        "aqi_color": ""

    }

    return weather


# ==========================================
# Weather Tips
# ==========================================

def add_weather_tip(weather):

    temp = weather["temperature"]
    humidity = weather["humidity"]
    main = weather["main"]

    if main == "Rain":
        weather["tip"] = "☔ Carry an umbrella today."

    elif main == "Thunderstorm":
        weather["tip"] = "⛈ Stay indoors if possible."

    elif main == "Snow":
        weather["tip"] = "❄ Roads may be slippery."

    elif temp >= 35:
        weather["tip"] = "🥤 Stay hydrated today."

    elif temp <= 10:
        weather["tip"] = "🧥 A jacket is recommended."

    elif humidity >= 85:
        weather["tip"] = "💧 It'll feel very humid."

    else:
        weather["tip"] = "🚶 Perfect weather for outdoor plans."

    return weather


# ==========================================
# AQI
# ==========================================

def get_aqi(weather):

    url = (
        "https://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={weather['lat']}"
        f"&lon={weather['lon']}"
        f"&appid={API_KEY}"
    )

    response = requests.get(url).json()

    weather["aqi"] = response["list"][0]["main"]["aqi"]

    levels = {

        1: ("Good", "#2ecc71"),
        2: ("Fair", "#f1c40f"),
        3: ("Moderate", "#e67e22"),
        4: ("Poor", "#e74c3c"),
        5: ("Very Poor", "#8e44ad")

    }

    weather["aqi_text"] = levels[weather["aqi"]][0]
    weather["aqi_color"] = levels[weather["aqi"]][1]

    return weather


# ==========================================
# Forecast
# ==========================================

def get_forecast(city):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(url)

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

                "description": item["weather"][0]["description"].title(),

                "icon": item["weather"][0]["icon"],

                "pop": int(item["pop"] * 100)

            })

            if len(forecast) == 5:
                break

    return forecast

def get_rain_chance(city):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(url)

    data = response.json()

    today = datetime.now().strftime("%Y-%m-%d")

    highest = 0

    for item in data["list"]:

        if item["dt_txt"].startswith(today):

            highest = max(

                highest,

                int(item["pop"] * 100)

            )

    return highest

# ==========================================
# Home
# ==========================================

@app.route("/", methods=["GET", "POST"])
def home():

    weather = session.pop("weather", None)
    forecast = session.pop("forecast", [])

    if request.method == "POST":

        city = request.form["city"].strip()

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}"
            f"&appid={API_KEY}"
            "&units=metric"
        )

        response = requests.get(url)

        if response.status_code == 200:

            weather = build_weather(response.json())

            weather = add_weather_tip(weather)

            weather = get_aqi(weather)

            forecast = get_forecast(weather["city"])

            weather["rain_chance"] = get_rain_chance(
                weather["city"]
            )

        else:

            weather = {
                "error": "City not found."
            }

            forecast = []

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast

    )

# ==========================================
# Weather Route
# ==========================================

@app.route("/weather/<city>")
def weather(city):

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:

        return render_template(

            "index.html",

            weather={
                "error": "City not found."
            },

            forecast=[]

        )

    weather = build_weather(response.json())

    weather = add_weather_tip(weather)

    weather = get_aqi(weather)
    forecast = get_forecast(weather["city"])

    weather["rain_chance"] = get_rain_chance(weather["city"])

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast

    )

# ==========================================
# Current Location
# ==========================================

@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:

        session["weather"] = {
            "error": "Unable to fetch location weather."
        }

        session["forecast"] = []

        return redirect("/")

    weather = build_weather(response.json())

    weather = add_weather_tip(weather)

    weather = get_aqi(weather)

    forecast = get_forecast(weather["city"])

    weather["rain_chance"] = get_rain_chance(
        weather["city"]
    )

    session["weather"] = weather
    session["forecast"] = forecast

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)