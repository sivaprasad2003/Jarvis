# core/connectivity_control.py
import pyautogui
import time
from core.speech import speak

def toggle_wifi():
    speak("Toggling Wi-Fi.")
    pyautogui.hotkey('win', 'a')  # Open Action Center
    pyautogui.press('space')  # Toggle Wi-Fi
    speak("Wi-Fi state changed, sir.")
    pyautogui.press('esc')  # Close Action Center

def toggle_bluetooth():
    speak("Toggling Bluetooth.")
    pyautogui.hotkey('win', 'a')
    time.sleep(1)
    pyautogui.press('right')  # Navigate to Bluetooth
    pyautogui.press('space')
    speak("Bluetooth status updated.")
    pyautogui.press('esc')

def toggle_airplane_mode():
    try:
        speak("Toggling airplane mode.")
        # Open Action Center (Windows + A)
        pyautogui.hotkey('win', 'a')
        icon_location = pyautogui.locateOnScreen('airplane.png', confidence=0.8)
        if icon_location:
            pyautogui.click(pyautogui.center(icon_location))
        time.sleep(1)
        pyautogui.hotkey('win', 'a')  # Close Action Center again
        speak("Airplane mode toggled.")
    except Exception as e:
        speak("Sorry, I couldn't toggle airplane mode.")
        print("[ERROR] Airplane toggle:", e)