# core/media_control.py
import pyautogui
import time
import os

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except Exception as e:
    print(f"[Warning] PyCAW audio control unavailable: {e}")
    PYCAW_AVAILABLE = False

from core.speech import speak
import pywhatkit
import webbrowser
import keyboard
# Safe Volume Setup
def play_pause_media():
    try:
        keyboard.send("play/pause media")
    except Exception as e:
        speak("Failed to toggle playback.")
        print(f"[Media Toggle Error] {e}")

def parse_volume_percentage(command: str):
    import re
    match = re.search(r'(\d+)\s*%?', command)
    if match:
        return int(match.group(1))
    return None

def set_volume(percent):
    if not PYCAW_AVAILABLE:
        speak("Volume control is unavailable on this system version.")
        return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        volume = max(0.0, min(percent / 100.0, 1.0))
        volume_interface.SetMasterVolumeLevelScalar(volume, None)
        speak(f"Volume set to {percent}%")
    except Exception as e:
        speak("Failed to set volume.")
        print(f"[Set Volume Error] {e}")

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

def play_song_on_youtube(song_name):
    try:
        speak(f"Searching {song_name} on YouTube.")
        pywhatkit.playonyt(song_name)
    except Exception as e:
        speak("YouTube playback failed.")
        print("[CRITICAL ERROR] YouTube fallback:", e)

def mute():
    pyautogui.press("volumemute")

def unmute():
    pyautogui.press("volumemute")   

def next_song():
    speak("Playing next track.")
    pyautogui.hotkey("ctrl", "right")

def prev_song():
    speak("Playing previous track.")
    pyautogui.hotkey("ctrl", "left")
