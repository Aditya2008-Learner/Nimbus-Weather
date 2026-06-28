from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

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

    weather = None

    if request.method == "POST":

        city = request.form["city"]

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather = build_weather(data)
        else:
            weather = {
                "error": "City not found."
            }

    return render_template("index.html", weather=weather)


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
    else:
        weather = {
            "error": "Unable to fetch location weather."
        }

    return render_template("index.html", weather=weather)


if __name__ == "__main__":
    app.run(debug=True)