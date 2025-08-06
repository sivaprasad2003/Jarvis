# core/system_status.py
import wmi
import psutil
from core.speech import speak
from core.utils import handle_error

try:
    import wmi  # For temperature and fan speed on Windows
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

def report_system_status():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        speak(f"CPU usage is at {cpu} percent.")
        speak(f"RAM usage is at {ram} percent.")
        speak(f"Disk usage is at {disk} percent.")

        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "charging" if battery.power_plugged else "not charging"
            speak(f"Battery is at {percent} percent and it is {plugged}.")

        if WMI_AVAILABLE:
            check_cpu_temperature()
            check_fan_speed()
        else:
            speak("Advanced hardware monitoring is unavailable. Please install WMI support for temperature and fan speed data.")

    except Exception as e:
        handle_error("system_status", e)
        speak("Sorry, I couldn't fetch complete system status.")

def check_cpu_temperature():
    try:
        w = wmi.WMI(namespace="root\wmi")
        
        # Temperature
        temperature_data = w.MSAcpi_ThermalZoneTemperature()
        if temperature_data:
            temp_kelvin = temperature_data[0].CurrentTemperature
            celsius = (temp_kelvin / 10.0) - 273.15
            speak(f"Current CPU temperature is {round(celsius)} degrees Celsius.")

            if celsius > 90:
                speak("⚠️ CPU temperature is dangerously high. Immediate action is recommended.")
                speak("Suggestion: Close background applications, clean your laptop vents, or check your cooling fan.")
            elif celsius > 80:
                speak("⚠️ CPU is running hot. Consider improving ventilation or reducing load.")
            elif celsius > 70:
                speak("Temperature is slightly elevated. No action needed yet, but keep an eye on it.")
            else:
                speak("CPU temperature is within safe operational limits.")

        else:
            speak("Unable to retrieve CPU temperature.")
    except Exception as e:
        handle_error("check_cpu_temperature", e)


def check_fan_speed():
        try:
            fans = w.Win32_Fan()
            if fans:
                for fan in fans:
                    rpm = fan.DesiredSpeed
                    if rpm:
                        speak(f"Fan is spinning at {rpm} RPM.")
                    else:
                        speak("Fan speed detected but RPM data unavailable.")
            else:
                speak("Fan information is not accessible.")
        except Exception as e:
            handle_error("check_fan_speed", e)
    
