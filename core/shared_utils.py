# core/shared_utils.py
from core.speech import speak, listen
from core.config import WAKE_WORD, AI_MODE, STANDBY_MODE, MEMORY_STORE
from core.object_detection import detect_objects, voice_listener, ensure_yolo_files, stop_detection_event
from core.memory import remember_this, recall_memory
from core.media_control import play_pause_media, prev_song, volume_up, volume_down, mute, next_song, unmute, set_volume, parse_volume_percentage
from core.gemini_ai import ask_gemini_fallback
from core.utils import handle_error
from core.screenshot import take_screenshot, show_last_screenshot, open_screenshot_folder
from core.battery_health import report_battery_health
import os
import webbrowser
import psutil
import datetime

def jarvis_main():
    speak("Jarvis online and ready.")
    while True:
        try:
            command = listen()
            if not command:
                continue

            # === SYSTEM CONTROL ===
            if "shutdown system" in command or "shutdown main system" in command:
                speak("Shutting down the system.")
                os.system("shutdown /s /t 1")

            elif "restart system" in command or "restart main system" in command:
                speak("Restarting the system.")
                os.system("shutdown /r /t 1")

            elif "hibernate system" in command or "hibernate main system" in command:
                speak("Hibernating the system.")
                os.system("shutdown /h")

            elif "lock system" in command or "lock main system" in command:
                speak("Locking your system.")
                os.system("rundll32.exe user32.dll,LockWorkStation")

            elif "object detection protocol" in command or "what do you see" in command:
                detect_objects()

            elif "stop object detection" in command:
                speak("Stopping object detection protocol.")
                stop_detection_event.set()

            elif "remember" in command:
                fact = command.replace("remember", "").strip()
                remember_this(fact)
            
            elif "battery report" in command or "battery health" in command:
                speak("Checking battery health.")
                report_battery_health()

            elif "what do you remember" in command:
                recall_memory()

            elif any(kw in command for kw in ["pause", "play", "resume media", "stop media"]):
                play_pause_media()    

            elif "set volume" in command:
                percent = parse_volume_percentage(command)
                if percent is not None:
                    set_volume(percent)
                else:
                    speak("Please specify the volume percent to set.")    

            elif "volume up" in command or "increase volume" in command:
                volume_up()

            elif "volume down" in command or "decrease volume" in command:
                volume_down()

            elif "mute" in command or "silence" in command:
                mute()

            elif "unmute" in command or "restore volume" in command:
                unmute()  

            elif "next song" in command or "skip song" in command:
                next_song()

            elif "previous song" in command or "go back to song " in command:
                prev_song()

            elif "take screenshot" in command:
                take_screenshot()

            elif "show last screenshot" in command:
                show_last_screenshot()

            elif "open screenshot folder" in command:
                open_screenshot_folder()

            # === OPEN APPS / SITES ===
            elif "open youtube" in command:
                webbrowser.open("https://www.youtube.com")
                speak("Opening YouTube.")

            elif "open google" in command:
                webbrowser.open("https://www.google.com")
                speak("Opening Google.")

            elif "open downloads" in command:
                downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                os.startfile(downloads)
                speak("Opening Downloads folder.")

            elif "open notepad" in command:
                os.system("start notepad")

            elif "open calculator" in command:
                os.system("start calc")   

            elif "jarvis are you there" in command:
                speak("At your service sir.")    

            elif "open" in command:
                app_name = command.replace("open", "").strip()
                speak(f"Opening {app_name}")
                os.system(f'start {app_name}')

            # === SYSTEM INFO ===
            elif "system status" in command or "system info" in command:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    ram = psutil.virtual_memory().percent
                    disk = psutil.disk_usage('/').percent

                    speak(f"CPU usage is at {cpu} percent.")
                    speak(f"RAM usage is at {ram} percent.")
                    speak(f"Disk usage is at {disk} percent.")

                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        plugged = "charging" if battery.power_plugged else "not charging"
                        speak(f"Battery is at {percent} percent and it is {plugged}.")
                except Exception as e:
                    handle_error("system_status", e)
                    speak("Sorry, I couldn't fetch system status.")

            elif "time" in command:
                now = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {now}.")

            elif "date" in command:
                today = datetime.date.today().strftime("%B %d, %Y")
                speak(f"Today is {today}.")

            elif "day" in command:
                day = datetime.datetime.now().strftime("%A")
                speak(f"Today is {day}.")
    
            # === AI MODE ===
            elif "activate ai mode" in command or "enter gemini" in command:
                speak("AI Mode activated. Ask me anything.")
                while True:
                    ai_command = listen()
                    if "deactivate ai mode" in ai_command or "leave gemini" in ai_command:
                        speak("Exiting AI Mode.")
                        break
                    elif ai_command:
                        reply = ask_gemini_fallback(ai_command)
                        speak(reply)

            # === EXIT / SHUTDOWN ===
            elif "exit yourself jarvis" in command or "close jarvis subsystem" in command:
                speak("Shutting down jarvis systems, Goodbye sir.")
                break

            else:
                speak("Command not recognized. Please try again.")

        except Exception as e:
            handle_error("jarvis_main", e)
