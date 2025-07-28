import pyautogui
from PIL import Image
import datetime
import os
import glob
import subprocess
from core.speech import speak

SCREENSHOT_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot():
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
        image = pyautogui.screenshot()
        image.save(path)
        speak(f"Screenshot taken and saved at Screenshots folder.")
    except Exception as e:
        speak("Failed to take screenshot.")
        print(f"[Screenshot Error] {e}")

def show_last_screenshot():
    try:
        files = sorted(glob.glob(os.path.join(SCREENSHOT_DIR, "*.png")), key=os.path.getmtime, reverse=True)
        if files:
            screenshot = files[0]
            os.startfile(screenshot)
            speak("Showing the most recent screenshot.")
        else:
            speak("No screenshots found.")
    except Exception as e:
        speak("Unable to open screenshot.")
        print(f"[Screenshot Open Error] {e}")

def open_screenshot_folder():
    try:
        os.startfile(SCREENSHOT_DIR)
        speak("Opening the screenshot folder.")
    except Exception as e:
        speak("Failed to open the screenshot directory.")
        print(f"[Folder Open Error] {e}")
