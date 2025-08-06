# core/weather.py
import requests
from core.speech import speak
from core.utils import handle_error
from core.config import OPENWEATHERMAP_API_KEY

# Replace with your actual OpenWeatherMap API key
WEATHER_API_KEY = OPENWEATHERMAP_API_KEY

def get_location_by_ip():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        city = data.get("city")
        return city
    except Exception as e:
        handle_error("get_location_by_ip", e)
        return None

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        weather_data = response.json()
        return weather_data
    except Exception as e:
        handle_error("get_weather", e)
        return None

def speak_weather():
    try:
        city = get_location_by_ip()
        if not city:
            speak("I'm unable to determine your location at the moment.")
            return

        weather_data = get_weather(city)
        if not weather_data or weather_data.get("cod") != 200:
            speak("I encountered a problem retrieving the weather, sir.")
            return

        condition = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        speak(f"Current weather in {city}: {condition.capitalize()} with a temperature of {temp}°C.")
        speak(f"It feels like {feels_like}°C with {humidity}% humidity. Wind speed is {wind_speed} meters per second.")

        if "rain" in condition:
            speak("You might want to carry an umbrella, sir. There's rain in the area.")
        else:
            speak("No rain is expected right now. You’re good to go, sir.")

    except Exception as e:
        handle_error("speak_weather", e)

def will_it_rain():
    try:
        city = get_location_by_ip()
        if not city:
            speak("I'm unable to determine your location for rain forecasting.")
            return

        weather_data = get_weather(city)
        if not weather_data or weather_data.get("cod") != 200:
            speak("I couldn't access forecast data, sir.")
            return

        condition = weather_data['weather'][0]['description']
        if "rain" in condition.lower():
            speak("Yes sir, there's a chance of rain today. Best to stay prepared.")
        else:
            speak("Negative sir, no rain detected in today's forecast.")
    except Exception as e:
        handle_error("will_it_rain", e)
