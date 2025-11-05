# core/system_status.py (Revised)
import wmi
import psutil
from core.speech import speak
from core.utils import handle_error # Assuming handle_error exists in core.utils

# Check WMI availability only once
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

def get_wmi_object(namespace="root\wmi"):
    """Function to safely get WMI object for a specific namespace."""
    try:
        return wmi.WMI(namespace=namespace)
    except Exception as e:
        # handle_error is called inside the exception, as intended by the original code structure.
        handle_error(f"WMI connection {namespace}", e)
        return None

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
    # Connect to the WMI namespace specific for thermal data.
    w_wmi = get_wmi_object(namespace="root\wmi")
    if not w_wmi:
        speak("Unable to connect to WMI for CPU temperature data.")
        return

    try:
        temperature_data = w_wmi.MSAcpi_ThermalZoneTemperature()
        
        if temperature_data:
            max_celsius = -float('inf')
            
            # Iterate through all reported thermal zones to find the highest temp
            for temp_zone in temperature_data:
                temp_kelvin_tenths = getattr(temp_zone, 'CurrentTemperature', None)
                if temp_kelvin_tenths is not None:
                    # Convert from tenths of a Kelvin to Celsius
                    celsius = (temp_kelvin_tenths / 10.0) - 273.15
                    if celsius > max_celsius:
                        max_celsius = celsius

            if max_celsius != -float('inf'):
                celsius = round(max_celsius)
                speak(f"Current System temperature is approximately {celsius} degrees Celsius.")

                # Status reporting logic
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
                 speak("Unable to retrieve valid CPU temperature data from thermal zones.")

        else:
            speak("Unable to retrieve CPU temperature.")
    except Exception as e:
        handle_error("check_cpu_temperature", e)
        speak("An error occurred while checking CPU temperature.")


def check_fan_speed():
    # Connect to the default WMI namespace (CIMV2) for hardware information.
    w_cimv2 = get_wmi_object(namespace="root\cimv2")
    if not w_cimv2:
        speak("Unable to connect to WMI for fan speed data.")
        return

    try:
        fans = w_cimv2.Win32_Fan()
        if fans:
            for fan in fans:
                # Win32_Fan is often unreliable. Using 'DesiredSpeed' as in original logic, but now on correct connection.
                rpm = getattr(fan, 'DesiredSpeed', None)
                if rpm:
                    speak(f"Fan is spinning at a reported speed of {rpm} RPM.")
                else:
                    speak(f"Fan detected, but specific speed data is unavailable.")
        else:
            speak("Fan information is not accessible. (Win32_Fan WMI class not reporting data).")
    except Exception as e:
        handle_error("check_fan_speed", e)
        speak("An error occurred while checking fan speed.")