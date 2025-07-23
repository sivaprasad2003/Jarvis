# core/shared_utils.py
from core.speech import speak, listen
from core.config import WAKE_WORD, AI_MODE, STANDBY_MODE, MEMORY_STORE
from core.object_detection import detect_objects
from core.memory import remember_this, recall_memory
from core.media_control import play_youtube, prev_song, volume_up, volume_down, mute, next_song
from core.gemini_ai import ask_gemini_fallback
from core.utils import handle_error
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
            if "shutdown" in command:
                speak("Shutting down the system.")
                os.system("shutdown /s /t 1")

            elif "restart" in command:
                speak("Restarting the system.")
                os.system("shutdown /r /t 1")

            elif "sleep" in command or "hibernate" in command:
                speak("Hibernating the system.")
                os.system("shutdown /h")

            elif "lock system" in command:
                speak("Locking your system.")
                os.system("rundll32.exe user32.dll,LockWorkStation")

            elif "detect object" in command or "what do you see" in command:
                detect_objects()

            elif "remember" in command:
                fact = command.replace("remember", "").strip()
                remember_this(fact)

            elif "what do you remember" in command:
                recall_memory()

            elif "volume up" in command:
                volume_up()

            elif "volume down" in command:
                volume_down()

            elif "mute" in command:
                mute()

            elif "next" in command:
                next_song()

            elif "previous" in command:
                prev_song()

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
            elif "exit" in command or "quit" in command or "stop" in command:
                speak("Goodbye sir. Shutting down.")
                break

            else:
                speak("Command not recognized. Please try again.")

        except Exception as e:
            handle_error("jarvis_main", e)
