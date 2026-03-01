# main.py
from core.speech import speak
from core.face_auth import face_login, welcome_greeting
from core.shared_utils import jarvis_main
from core.utils import handle_error, setup_global_exception_hook
from core.battery_monitor import check_battery_alert, start_battery_monitor
from core.system_status import start_hardware_monitoring
from core.gui import run_jarvis_thread

if __name__ == "__main__":
    setup_global_exception_hook()
    speak("Initializing JARVIS core systems...")
    start_battery_monitor()
    start_hardware_monitoring()
    try:
        if face_login():
            welcome_greeting()
            jarvis_main()  
    except KeyboardInterrupt:
        speak("Manual override engaged. JARVIS shutting down.")
    except Exception as main_error:
        handle_error("main", main_error)
