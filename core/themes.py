# core/theme_control.py
import pyautogui
import time
from core.speech import speak

def switch_to_dark_mode():
    speak("Switching to dark mode interface.")
    pyautogui.hotkey('win', 'i')  # Open settings
    time.sleep(2)
    pyautogui.write('choose your mode')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.press('tab', presses=9, interval=0.1)  # Tab to dropdown
    pyautogui.press('down')  # Select dark mode
    speak("Dark mode activated, sir.")
    pyautogui.hotkey('alt', 'f4')  # Close settings

def switch_to_light_mode():
    speak("Reverting to light mode interface.")
    pyautogui.hotkey('win', 'i')
    time.sleep(2)
    pyautogui.write('choose your mode')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.press('tab', presses=9, interval=0.1)
    pyautogui.press('up')  # Select light mode
    speak("Light mode engaged, sir.")
    pyautogui.hotkey('alt', 'f4')
