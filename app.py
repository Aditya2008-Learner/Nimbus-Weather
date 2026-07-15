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

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
BASE_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
BASE_AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
# ==========================================
# Helper Functions
# ==========================================

def format_time(timestamp: int, timezone_offset: int) -> str:
    """Convert UNIX timestamp into local city time."""

    city_timezone = timezone(timedelta(seconds=timezone_offset))

    return datetime.fromtimestamp(
        timestamp,
        tz=city_timezone
    ).strftime("%I:%M %p")


def build_weather(data: dict) -> dict:
    """Build a clean weather dictionary for templates."""
    
    temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    weather_main = data["weather"][0]["main"].lower()
    
    tip = "🌤️ Conditions are stable. Have a wonderful day!"
    if "rain" in weather_main or "drizzle" in weather_main:
        tip = "☔ Rain detected. Grabbing an umbrella is a smart move today."
    elif humidity > 80 and temp > 25:
        tip = "💧 High humidity day. Stay hydrated and stick to cooler indoor areas."
    elif temp > 32:
        tip = "☀️ High temperatures outside. Seek shade and keep water nearby."
    elif temp < 10:
        tip = "🧥 It's quite chilly out. Layer up before heading out."

    uv_val = data.get("uvi", data.get("main", {}).get("uvi", 3.5)) 
    
    if uv_val < 3:
        uv_status = "🟢 Low Risk"
        uv_advice = "Safe to stay outside without extra protection."
    elif uv_val < 6:
        uv_status = "🟡 Moderate Risk"
        uv_advice = "Apply SPF 15+ if staying outdoors for long."
    elif uv_val < 8:
        uv_status = "🟠 High Risk"
        uv_advice = "Seek shade during midday. Protection required."
    else:
        uv_status = "🔴 Very High / Extreme"
        uv_advice = "Minimize sun exposure between 10 AM - 4 PM. Wear SPF 30+."

    weather = {

    "uv_index": round(uv_val, 1),
        "uv_status": uv_status,
        "uv_advice": uv_advice,
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": temp,
        "feels_like": round(data["main"]["feels_like"]),
        "temp_min": round(data["main"]["temp_min"]),
        "temp_max": round(data["main"]["temp_max"]),
        "humidity": humidity,
        "pressure": data["main"]["pressure"],
        "visibility": round(data["visibility"] / 1000),
        "clouds": data["clouds"]["all"],
        "wind": round(data["wind"]["speed"], 1),
        
        "wind_deg": data["wind"].get("deg", 0),

        "main": data["weather"][0]["main"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "sunrise": format_time(data["sys"]["sunrise"], data["timezone"]),
        "sunset": format_time(data["sys"]["sunset"], data["timezone"]),
        "is_day": data["sys"]["sunrise"] <= data["dt"] <= data["sys"]["sunset"],
        
        "tip": tip,
        "greeting": "",
        "rain_chance": 0,
    }

    return weather

# ==========================================
# API SERVICE FUNCTIONS
# ==========================================

def get_weather(city):

    response = requests.get(

        BASE_WEATHER_URL,

        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

    )

    return response


def get_weather_by_location(lat, lon):

    response = requests.get(

        BASE_WEATHER_URL,

        params={
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }

    )

    return response


def get_forecast(city):

    response = requests.get(

        BASE_FORECAST_URL,

        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

    )

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


def get_hourly_forecast(city):

    response = requests.get(

        BASE_FORECAST_URL,

        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

    )

    data = response.json()

    hourly = []

    for item in data["list"][:8]:

        hourly.append({

            "time": datetime.strptime(
                item["dt_txt"],
                "%Y-%m-%d %H:%M:%S"
            ).strftime("%I %p"),

            "temp": round(item["main"]["temp"]),

            "icon": item["weather"][0]["icon"],

            "pop": int(item["pop"] * 100)

        })

    return hourly


def get_aqi(weather):

    response = requests.get(

        BASE_AQI_URL,

        params={

            "lat": weather["lat"],

            "lon": weather["lon"],

            "appid": API_KEY

        }

    )

    data = response.json()

    weather["aqi"] = data["list"][0]["main"]["aqi"]

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
        weather["tip"] = "💧 It'll feel quite humid."

    else:
        weather["tip"] = "🚶 Perfect weather for outdoor plans."

    return weather


@app.route("/", methods=["GET", "POST"])
def home():

    weather = session.pop("weather", None)
    forecast = session.pop("forecast", [])
    hourly = session.pop("hourly", [])

    if request.method == "POST":

        city = request.form["city"].strip()

        response = get_weather(city)

        if response.status_code == 200:

            data = response.json()

            weather = build_weather(data)

            weather = get_aqi(weather)

            weather = add_weather_tip(weather)

            forecast = get_forecast(city)

            hourly = get_hourly_forecast(city)

            weather["rain_chance"] = max(

                (day["pop"] for day in forecast),

                default=0

            )

        else:

            weather = {

                "error": "City not found."

            }

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast,

        hourly=hourly

    )

@app.route("/weather/<city>")
def weather(city):

    response = get_weather(city)

    if response.status_code != 200:

        return render_template(

            "index.html",

            weather={
                "error": "City not found."
            },

            forecast=[],

            hourly=[]

        )

    data = response.json()

    weather = build_weather(data)

    weather = get_aqi(weather)

    weather = add_weather_tip(weather)

    forecast = get_forecast(city)

    hourly = get_hourly_forecast(city)

    weather["rain_chance"] = max(

        (day["pop"] for day in forecast),

        default=0

    )

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast,

        hourly=hourly

    )

@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    response = get_weather_by_location(lat, lon)

    if response.status_code != 200:

        session["weather"] = {
            "error": "Unable to fetch location weather."
        }

        session["forecast"] = []
        session["hourly"] = []

        return redirect("/")

    data = response.json()

    city = data["name"]

    weather = build_weather(data)

    weather = get_aqi(weather)

    weather = add_weather_tip(weather)

    forecast = get_forecast(city)

    hourly = get_hourly_forecast(city)

    weather["rain_chance"] = max(

        (day["pop"] for day in forecast),

        default=0

    )

    session["weather"] = weather
    session["forecast"] = forecast
    session["hourly"] = hourly

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)