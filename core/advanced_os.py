import pyautogui
import pyperclip
import winshell
import os
import tempfile
import time
from AppOpener import open as app_open # Better dynamic app opening

def type_dictation(text):
    """Allows Jarvis to physically type out what you say."""
    try:
        pyautogui.write(text, interval=0.03)
    except Exception as e:
        print(f"Typing error: {e}")

def window_control(action):
    """Deep control over Windows GUI."""
    if action == "switch":
        pyautogui.hotkey('alt', 'tab')
    elif action == "close":
        pyautogui.hotkey('alt', 'f4')
    elif action == "minimize all":
        pyautogui.hotkey('win', 'd')
    elif action == "maximize":
        pyautogui.hotkey('win', 'up')

def read_clipboard():
    """Reads whatever text you currently have copied."""
    text = pyperclip.paste()
    if text:
        return f"Clipboard reads: {text}"
    return "Your clipboard is currently empty, sir."

def empty_recycle_bin():
    """Empties the trash."""
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
        return "Recycle bin emptied. Storage optimized."
    except Exception:
        return "The recycle bin is already empty, sir."

def clear_temp_files():
    """Clears Windows Temp folder to speed up PC."""
    try:
        temp_dir = tempfile.gettempdir()
        os.system(f"del /q /f /s {temp_dir}\\*")
        return "Temporary files cleared successfully."
    except Exception as e:
        return "Failed to clear some temporary files. They might be in use."

def dynamic_app_launcher(app_name):
    """Replaces hardcoded app opening. Can open almost any installed app dynamically."""
    try:
        app_open(app_name, match_closest=True)
        return f"Opening {app_name}, sir."
    except Exception:
        return f"I could not locate {app_name} on your system."