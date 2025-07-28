import os
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
report_path = os.path.expanduser("C:\\Windows\\Temp\\battery-report.html")

from bs4 import BeautifulSoup

def extract_capacity_in_mwh(text):
    try:
        text = text.lower().replace('mwh', '').replace(',', '').strip()
        return int(text)
    except:
        return None

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

                        # Debug print
                        print(f"[DEBUG] Heading: {heading} | Value: {value}")

                        if "design capacity" in heading:
                            design_capacity = extract_capacity_in_mwh(value)
                            print(f"[✅] Design Capacity: {design_capacity} mWh")
                        elif "full charge capacity" in heading:
                            full_charge_capacity = extract_capacity_in_mwh(value)
                            print(f"[✅] Full Charge Capacity: {full_charge_capacity} mWh")

            if design_capacity and full_charge_capacity:
                percent = (full_charge_capacity / design_capacity) * 100
                print(f"[🔋] Battery Health is {round(percent, 2)}%")
            else:
                print("[⚠️] Could not find both capacities.")

    except Exception as e:
        print(f"[❌ ERROR] {e}")

# Run this
get_battery_health_percentage(report_path)

  
