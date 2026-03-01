import os
import time
import pyautogui

def open_windows_app(app_name):
    app_name = app_name.lower().strip()
    print(f"[App Launcher] Taking control of keyboard to search and launch: {app_name}")
    
    try:
        # Automated keyboard control macro sequence
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)
        pyautogui.press("enter")
        return True
    except Exception as e:
        print(f"Failed to execute keyboard macro for {app_name}: {e}")
        # Final fallback
        result = os.system(f"start {app_name}")
        return result == 0
