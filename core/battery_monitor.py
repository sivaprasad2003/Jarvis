import psutil
import threading
import time

# Shared alert state
battery_alert = {'active': False, 'message': ''}

def monitor_battery(threshold=85, check_interval=60):
    alerted = False
    global battery_alert
    while True:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged

            if plugged and percent >= threshold and not alerted:
                battery_alert['active'] = True
                battery_alert['message'] = f"Sir, Your Battery is at {percent} percent and charging. Consider unplugging the charger."
                alerted = True
            elif not plugged or percent < threshold:
                battery_alert['active'] = False
                battery_alert['message'] = ''
                alerted = False  # Reset alert when unplugged or below threshold
        time.sleep(check_interval)

def start_battery_monitor():
    thread = threading.Thread(target=monitor_battery, daemon=True)
    thread.start()

def check_battery_alert(speak_func):
    global battery_alert
    if battery_alert['active'] and battery_alert['message']:
        speak_func(battery_alert['message'])
        battery_alert['active'] = False
        battery_alert['message'] = ''
