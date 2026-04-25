# core/system_status.py (Revised)
import wmi
import sys
import psutil
import threading
import time
from core.speech import speak
from core.utils import handle_error # Assuming handle_error exists in core.utils

# Check WMI availability only once
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

def get_wmi_object(namespace=r"root\wmi"):
    """Function to safely get WMI object for a specific namespace."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
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
    cpu_temperature = None
    try:
        w_wmi = wmi.WMI()
        # Attempt to get temperature using MSAcpi_ThermalZoneTemperature
        # This class is often unreliable, requires specific permissions, or specific drivers.
        temperature_data = w_wmi.MSAcpi_ThermalZoneTemperature()
        
        if temperature_data:
            # WMI returns temperature in Kelvin * 10.
            # Convert to Celsius: (K / 10) - 273.15
            # Example: if CurrentTemperature is 2982 (298.2 K), then (298.2) - 273.15 = 25.05 C
            cpu_temperature = (temperature_data[0].CurrentTemperature / 10.0) - 273.15
        else:
            print("No CPU temperature data found via MSAcpi_ThermalZoneTemperature.", file=sys.stderr)
            
    except wmi.x_access_denied:
        print("WMI Access Denied: Could not retrieve CPU temperature. This WMI class (MSAcpi_ThermalZoneTemperature) might not be available/supported on your system, or the script might need to be run with elevated administrator privileges.", file=sys.stderr)
        cpu_temperature = None
    except wmi.x_wmi as e:
        # Catch other WMI-specific errors
        print(f"WMI error while checking CPU temperature: {e}", file=sys.stderr)
        cpu_temperature = None
    except IndexError:
        # This can happen if temperature_data is an empty list, even if it passes the `if temperature_data:` check
        # (e.g., if it's an empty list but not considered False in some edge cases, or if other list access errors occur)
        print("CPU temperature data was returned but it was empty or malformed (IndexError).", file=sys.stderr)
        cpu_temperature = None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred while trying to get CPU temperature: {e}", file=sys.stderr)
        cpu_temperature = None

    return cpu_temperature


def check_fan_speed():
    # Connect to the default WMI namespace (CIMV2) for hardware information.
    w_cimv2 = get_wmi_object(namespace=r"root\cimv2")
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

monitoring_thread = None

def hardware_monitor_loop():
    while True:
        try:
            if WMI_AVAILABLE:
                w_wmi = get_wmi_object(namespace=r"root\wmi")
                if w_wmi:
                    temp_data = w_wmi.MSAcpi_ThermalZoneTemperature()
                    if temp_data:
                        max_celsius = -float('inf')
                        for temp_zone in temp_data:
                            tk = getattr(temp_zone, 'CurrentTemperature', None)
                            if tk is not None:
                                c = (tk / 10.0) - 273.15
                                if c > max_celsius:
                                    max_celsius = c
                        if max_celsius > 90:
                            speak(f"Warning! CPU temperature is critically high at {int(max_celsius)} degrees Celsius.")
        except:
            pass
        time.sleep(300) # Check every 5 minutes

def start_hardware_monitoring():
    global monitoring_thread
    if monitoring_thread is None or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(target=hardware_monitor_loop, daemon=True)
        monitoring_thread.start()