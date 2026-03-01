# core/shared_utils.py
from core.speech import speak, listen, start_listening_thread, get_next_command, stop_listening_thread
import core.speech as speech
from core.config import WAKE_WORD, AI_MODE, STANDBY_MODE, MEMORY_STORE
from core.object_detection import detect_objects, ensure_yolo_files, stop_detection_event
from core.memory import remember_this, recall_memory
from core.media_control import play_pause_media, prev_song, volume_up, volume_down, mute, next_song, unmute, set_volume, parse_volume_percentage
from core.gemini_ai import ask_gemini_fallback
from core.utils import handle_error
from core.screenshot import take_screenshot, show_last_screenshot, open_screenshot_folder
from core.battery_health import report_battery_health
from core.speed_test import run_speed_test
from core.battery_monitor import check_battery_alert
from core.weather import speak_weather, will_it_rain
from core.search import handle_search
from core.system_status import report_system_status, check_cpu_temperature, check_fan_speed
from core.ip_location_info import get_ip_address, get_location
from core.themes import switch_to_dark_mode, switch_to_light_mode
from core.connectivity import toggle_bluetooth, toggle_wifi
from core.media_control import play_song_on_youtube
from core.app_launcher import open_windows_app

import os
import webbrowser
import psutil
import datetime
import requests
import threading

def jarvis_main():
    speak("Jarvis online and ready.")
    start_listening_thread()
    ai_mode_active = False
    speech.REQUIRE_WAKE_WORD = True
    while True:
        try:
            check_battery_alert(speak)
            command = get_next_command(timeout=1.0)
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

            elif "object detection" in command or "start object detection" in command:
                detect_objects()

            elif "what do you see" in command or "what is this" in command:
                from core.object_detection import detected_labels
                if detected_labels:
                    speak(f"I see: {', '.join(set(detected_labels))}")
                else:
                    speak("I don't see anything notable right now.")

            elif "stop object detection" in command:
                stop_detection_event.set()
                speak("Stopped object detection.")

            elif "remember" in command:
                fact = command.replace("remember", "").strip()
                remember_this(fact)

            elif "enable dark mode" in command or "activate dark mode" in command:
                switch_to_dark_mode()

            elif "enable light mode" in command or "activate light mode" in command:
                switch_to_light_mode()

            elif "enable wifi" in command or "disable wifi" in command:
                toggle_wifi()

            elif "enable bluetooth" in command or "disable bluetooth" in command:
                toggle_bluetooth()    
            
            elif "battery report" in command or "battery health" in command:
                speak("Checking battery health.")
                report_battery_health()

            elif "what do you remember" in command:
                recall_memory()

            elif any(kw in command for kw in ["pause media", "play media", "resume media", "stop media"]):
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

            elif "ip address" in command:
                get_ip_address()

            elif "location" in command:
                get_location()

            elif "play" in command and "on youtube" in command:
                song = command.replace("play", "").replace("on youtube", "").strip()
                if song:
                    play_song_on_youtube(song)
                else:
                    speak("Please specify the song name to play.")
    
            elif "open downloads" in command:
                downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                os.startfile(downloads)
                speak("Opening Downloads folder.")

            elif "open notepad" in command:
                os.system("start notepad")

            elif "open calculator" in command:
                os.system("start calc")   

            elif "are you there" in command:
                speak("At your service sir.")    

            elif "open" in command:
                app_name = command.replace("open", "").strip()
                if app_name:
                    speak(f"Attempting to open {app_name}")
                    success = open_windows_app(app_name)
                    if not success:
                        speak(f"Could not find or open application {app_name}.")
                    else:
                        speak(f"Done.")   
                    

            elif "who are you" in command or "tell me about yourself" in command:
                speak("I am JARVIS, your personal AI assistant, designed with inspiration of Tony Stark. At your service, sir.")
            elif "are you iron man" in command:
                speak("I am not Iron Man, but I do serve him. You, however, are my priority.")
            elif "do you love pepper" in command:
                speak("As an AI, I do not possess feelings, but Miss Potts is highly valued by Mr. Stark.")

            # === REMINDERS & ALARMS ===
            elif "set reminder for" in command:
                import re, threading
                match = re.search(r"set reminder for (\d+) (second|seconds|minute|minutes|hour|hours)", command)
                if match:
                    value, unit = int(match.group(1)), match.group(2)
                    seconds = value * (3600 if 'hour' in unit else 60 if 'minute' in unit else 1)
                    def reminder():
                        speak("Reminder: Time's up!")
                    threading.Timer(seconds, reminder).start()
                    speak(f"Reminder set for {value} {unit}.")
                else:
                    speak("Please specify the time for the reminder, e.g., 'set reminder for 5 minutes'.")

            # === JOKES ===
            elif "tell me a joke" in command:
                jokes = [
                    "Why did Tony Stark always carry a pencil? In case he had to draw his suit.",
                    "Why did Jarvis go to school? To become a smarter AI.",
                    "I would tell you a UDP joke, but you might not get it."
                ]
                import random
                speak(random.choice(jokes))

            # === NEWS ===
            elif "tell me the news" in command or "news" in command:
                try:
                    from core.config import NEWSAPI_KEY
                    news_api = NEWSAPI_KEY # Replace with your free API key
                    response = requests.get(news_api)
                    articles = response.json().get("articles", [])
                    if articles:
                        speak("Here are the top headlines:")
                        for article in articles[:3]:
                            speak(article.get("title", "No title available."))
                    else:
                        speak("Sorry, I couldn't fetch the news right now.")
                except Exception as e:
                    handle_error("news", e)
                    speak("News service error.")    

            elif "system status" in command or "system info" in command:
                report_system_status()
                check_cpu_temperature()
                check_fan_speed()

            elif "check cpu temperature" in command:
                check_cpu_temperature()

            elif "check fan speed" in command:
                check_fan_speed()      

            elif "speed test" in command or "internet speed" in command:
                run_speed_test()          

            elif "what time" in command:
                now = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {now}.")

            elif "what date today" in command or "what day today" in command:
                today = datetime.date.today()
                speak(f"Today is {today.strftime('%A, %B %d, %Y')}.")

            elif "what was yesterday's date" in command or "yesterday what date" in command or "what was yesterday's day" in command or "yesterday what day" in command:
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                speak(f"Yesterday was {yesterday.strftime('%A, %B %d, %Y')}.")

            elif "what is tomorrow's date" in command or "tomorrow what date" in command or "what is tomorrow's date" in command or "tomorrow what date" in command:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                speak(f"Tomorrow will be {tomorrow.strftime('%A, %B %d, %Y')}.")

            elif any(kw in command for kw in ["search google for", "search amazon for", "search flipkart for"]):
                handle_search(command) 

            elif "weather" in command:
                speak_weather()

            elif "will it rain" in command or "rain today" in command:
                will_it_rain()
       
            # === AI MODE ===
            elif "activate ai mode" in command or "enter gemini" in command or "let's talk" in command:
                ai_mode_active = True
                speech.REQUIRE_WAKE_WORD = False
                speak("AI Mode activated. You can speak to me naturally now without saying Jarvis. How can I help you?")
                continue

            # Process any commands in AI mode if active, and handle deactivation
            if ai_mode_active:
                if "deactivate ai mode" in command or "leave gemini" in command or "exit ai mode" in command or "stop ai mode" in command or "goodbye" in command.lower():
                    ai_mode_active = False
                    speech.REQUIRE_WAKE_WORD = True
                    speak("Exiting AI conversational mode. Standard command protocols restored.")
                    continue
                
                # Exclude basic commands from accidentally triggering Gemini constantly
                local_commands = ["volume", "mute", "turn on", "turn off", "shutdown", "stop listening"]
                if not any(lc in command.lower() for lc in local_commands):
                    def process_gemini(query):
                        reply = ask_gemini_fallback(query)
                        speak(reply)
                        
                    threading.Thread(target=process_gemini, args=(command,), daemon=True).start()
                continue

            # === EXIT / SHUTDOWN ===
            elif "exit yourself jarvis" in command or "close jarvis subsystem" in command:
                speak("Shutting down jarvis systems, Goodbye sir.")
                stop_listening_thread()
                break

            elif "emergency stop" in command or "terminate protocol" in command:
                speak("Emergency stop engaged. Terminating all processes immediately.")
                from core.speech import stop_listening_thread
                from core.object_detection import stop_detection_event
                stop_detection_event.set()
                stop_listening_thread()
                import sys
                sys.exit(0)

            else:
                pass # Silently ignore ambient noise and unidentified chatter

        except Exception as e:
            handle_error("jarvis_main", e)
