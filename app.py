from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key for session
app.secret_key = os.getenv("SECRET_KEY")

API_KEY = os.getenv("API_KEY")


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

@app.route("/", methods=["GET", "POST"])
def home():

    # Weather from location redirect (shown once)
    weather = session.pop("weather", None)

    # Empty forecast list for now
    daily_forecast = []

    if request.method == "POST":

        city = request.form["city"]

        # Current weather API
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        # 5-day forecast API
        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        # Current weather
        response = requests.get(url)
        data = response.json()

        # Forecast
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        if response.status_code == 200:
            weather = build_weather(data)

            aqi_url = (
                "https://api.openweathermap.org/data/2.5/air_pollution"
                f"?lat={weather['lat']}"
                f"&lon={weather['lon']}"
                f"&appid={API_KEY}"
            )

            aqi_response = requests.get(aqi_url)
            aqi_data = aqi_response.json()

            weather["aqi"] = aqi_data["list"][0]["main"]["aqi"]

            aqi_levels = {
                1: ("Good", "#2ecc71"),
                2: ("Fair", "#f1c40f"),
                3: ("Moderate", "#e67e22"),
                4: ("Poor", "#e74c3c"),
                5: ("Very Poor", "#8e44ad")
            }

            weather["aqi_text"] = aqi_levels[weather["aqi"]][0]
            weather["aqi_color"] = aqi_levels[weather["aqi"]][1]

            # Get one forecast (12 PM) for each day
            daily_forecast = []

            for item in forecast_data["list"]:
                if "12:00:00" in item["dt_txt"]:
                    daily_forecast.append({
                        "day": datetime.strptime(
                            item["dt_txt"],
                            "%Y-%m-%d %H:%M:%S"
                        ).strftime("%a"),
                        "temp": round(item["main"]["temp"]),
                        "description": item["weather"][0]["description"].title(),
                        "icon": item["weather"][0]["icon"]
                    })
        else:
            weather = {
                "error": "City not found."
            }

    return render_template(
        "index.html",
        weather=weather,
        forecast=daily_forecast
    )

@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    print("Latitude:", lat)
    print("Longitude:", lon)
    print("Status:", response.status_code)
    print("Response:", data)

    if response.status_code == 200:
        weather = build_weather(data)

        aqi_url = (
            "https://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={weather['lat']}"
            f"&lon={weather['lon']}"
            f"&appid={API_KEY}"
        )

        aqi_response = requests.get(aqi_url)
        aqi_data = aqi_response.json()

        weather["aqi"] = aqi_data["list"][0]["main"]["aqi"]

        aqi_levels = {
            1: ("Good", "#2ecc71"),
            2: ("Fair", "#f1c40f"),
            3: ("Moderate", "#e67e22"),
            4: ("Poor", "#e74c3c"),
            5: ("Very Poor", "#8e44ad")
        }

        weather["aqi_text"] = aqi_levels[weather["aqi"]][0]
        weather["aqi_color"] = aqi_levels[weather["aqi"]][1]

        session["weather"] = weather
    else:
        session["weather"] = {
            "error": "Unable to fetch location weather."
        }

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)