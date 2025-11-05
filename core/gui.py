# core/gui.py (New/Revised - Eel Web GUI Launcher)
import eel
from threading import Thread
import os
from core.speech import speak
from core.shared_utils import jarvis_main

# Define the path to the frontend resources (relative to core/)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

def run_jarvis_thread():
    """Starts the main JARVIS assistant function."""
    speak("Starting voice assistant mode.")
    jarvis_main()

@eel.expose
def start_assistant_action():
    """Eel-exposed function called from JavaScript to start the main voice assistant."""
    # Run in a separate thread to prevent blocking the GUI/eel server
    Thread(target=run_jarvis_thread).start()

def launch_gui():
    """Initializes and launches the web-based J.A.R.V.I.S. GUI using eel."""
    try:
        # Initialize Eel, pointing to the frontend directory
        eel.init(FRONTEND_DIR)
        
        speak("Launching graphical interface in web browser.")
        
        # Start the web server and open the main HTML file
        # Using chrome-app mode provides a cleaner, dedicated application window
        eel.start('index.html', size=(1000, 700), mode='chrome-app')
        
    except Exception as e:
        speak(f"Error launching web GUI: {str(e)}. Please check your eel setup and try again.")
        raise e

# Note: The main.py file needs to call launch_gui()