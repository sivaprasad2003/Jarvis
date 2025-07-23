# core/media_control.py
import pyautogui
import time
from core.speech import speak

def play_youtube():
    speak("Playing video on YouTube.")
    pyautogui.press("k")  # Play/Pause

def volume_up():
    speak("Increasing volume.")
    for _ in range(5):
        pyautogui.press("volumeup")
        time.sleep(0.1)

def volume_down():
    speak("Decreasing volume.")
    for _ in range(5):
        pyautogui.press("volumedown")
        time.sleep(0.1)

def mute():
    speak("Muting volume.")
    pyautogui.press("volumemute")

def next_song():
    speak("Playing next track.")
    pyautogui.hotkey("ctrl", "right")

def prev_song():
    speak("Playing previous track.")
    pyautogui.hotkey("ctrl", "left")
