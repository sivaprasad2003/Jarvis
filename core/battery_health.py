from bs4 import BeautifulSoup
import os
import time
from core.speech import speak
from core.utils import handle_error

def extract_capacity_in_mwh(text):
    try:
        return int(text.lower().replace('mwh', '').replace(',', '').strip())
    except:
        return None
    
def get_battery_health_status(percent):
   
    if percent >= 95:
        return ("Optimal State","Battery is operating at peak condition — virtually untouched, like the day it was born.")
    elif percent >= 85:
        return ("Excellent State","Battery integrity remains strong, Minimal degradation observed. No cause for concern, sir.")
    elif percent >= 75:
        return ("Normal State","Battery is in fair shape. Some wear detected, but it remains mission-ready.")
    elif percent >= 65:
        return ("Below Average State","Noticeable wear on the battery. Not critical yet, but replacement should be considered in the near future.")
    elif percent >= 50:
        return ("Weak State","Power levels are suboptimal. Battery is aging and may result in reduced endurance. Proceed with caution.")
    else:
        return ("Critical","Battery degradation is severe. I strongly advise to replacement battery component, sir.")  

def get_battery_health_percentage(report_path):
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            tables = soup.find_all('table')

            design_capacity = None
            full_charge_capacity = None

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        heading = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        if "design capacity" in heading:
                            design_capacity = extract_capacity_in_mwh(value)
                        elif "full charge capacity" in heading:
                            full_charge_capacity = extract_capacity_in_mwh(value)

            if design_capacity and full_charge_capacity:
                return round((full_charge_capacity / design_capacity) * 100, 2)
            else:
                return None
    except Exception as e:
        handle_error("get_battery_health_percentage", e)
        return None

def report_battery_health():
    try:
        report_path = os.path.expanduser("C:\\Windows\\Temp\\battery-report.html")
        
        # Generate if missing
        if not os.path.exists(report_path):
            speak("Battery report not found. Generating one now.")
            os.system(f"powercfg /batteryreport /output \"{report_path}\"")
            time.sleep(2)

        percent = get_battery_health_percentage(report_path)

        if percent is not None:
            status, explanation = get_battery_health_status(percent)
            speak(f"Sir, your battery health is at {percent} percent and it is in {status}. {explanation}")
        else:
            speak("Could not retrieve battery health information.")
    except Exception as e:
        handle_error("report_battery_health", e)
        speak("Something went wrong while checking battery health.")
