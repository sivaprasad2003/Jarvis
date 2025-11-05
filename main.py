# main.py
from core.speech import speak, standby_mode
from core.face_auth import face_login, welcome_greeting
from core.shared_utils import jarvis_main
from core.utils import handle_error
from core.battery_monitor import check_battery_alert, start_battery_monitor
from core.gui import JarvisGUI, run_jarvis_thread

if __name__ == "__main__":

    speak("Initializing JARVIS core systems...")
    start_battery_monitor()
    try:
        if face_login():
            welcome_greeting()
            jarvis_main()  
    except KeyboardInterrupt:
        speak("Manual override engaged. JARVIS shutting down.")
    except Exception as main_error:
        handle_error("main", main_error)
