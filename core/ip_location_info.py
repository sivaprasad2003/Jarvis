import requests
from core.speech import speak
from core.utils import handle_error

def get_ip_address():
    try:
        ip = requests.get('https://api.ipify.org').text
        speak(f"Your IP address is {ip}")
        return ip
    except Exception as e:
        handle_error("get_ip_address", e)
        speak("I'm unable to fetch your IP address right now.")

def get_location():
    try:
        ip = requests.get('https://api.ipify.org').text
        location_data = requests.get(f'https://ipapi.co/{ip}/json/').json()

        city = location_data.get("city", "Unknown city")
        region = location_data.get("region", "Unknown region")
        country = location_data.get("country_name", "Unknown country")

        speak(f"You're currently in {city}, {region}, {country}.")
    except Exception as e:
        handle_error("get_location", e)
        speak("Sorry, I can't determine your location right now.")
