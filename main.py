# main.py
from core.speech import speak
from core.face_auth import face_login, welcome_greeting
from core.shared_utils import jarvis_main
# from core.gui import launch_gui
from core.utils import handle_error

if __name__ == "__main__":
    speak("Initializing JARVIS core systems...")
    try:
        if face_login():
            welcome_greeting()
            jarvis_main()
           # launch_gui()  
    except KeyboardInterrupt:
        speak("Manual override engaged. JARVIS shutting down.")
    except Exception as main_error:
        handle_error("main", main_error)
