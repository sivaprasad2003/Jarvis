# core/shared_utils.py
from core.speech import speak, listen, start_listening_thread, get_next_command, stop_listening_thread
import core.speech as speech
from core.config import WAKE_WORD, AI_MODE, STANDBY_MODE, MEMORY_STORE
from core.object_detection import detect_objects, ensure_yolo_files, stop_detection_event
from core.memory import remember_this, recall_memory
from core.media_control import play_pause_media, prev_song, volume_up, volume_down, mute, next_song, unmute, set_volume, parse_volume_percentage
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
from core.advanced_os import window_control
from core.advanced_os import read_clipboard
from core.advanced_os import empty_recycle_bin
from core.advanced_os import clear_temp_files
from core.advanced_os import dynamic_app_launcher
from core.advanced_os import type_dictation

import os
import webbrowser
import psutil
import datetime
import requests
import threading
import subprocess 
import time

# ==========================================
# OFFLINE AI ENGINE (OLLAMA + TINY MODEL)
# ==========================================
def preload_offline_ai():
    """Starts Ollama and pre-loads the model into RAM for instant responses."""
    speak("Initializing offline neural network. Please wait a moment.")

    
    try:
        requests.get("http://localhost:11434/", timeout=2)
    except requests.exceptions.ConnectionError:
        try:
            subprocess.Popen(["ollama", "serve"], shell=True)
            time.sleep(4)
        except Exception:
            speak("Failed to start Ollama server automatically. Please open it manually.")
            return

    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "tinyllama",
            "prompt": "system check",
            "stream": False,
            "keep_alive": -1 
        }
        requests.post(url, json=payload, timeout=120)
        speak("Neural network successfully loaded into memory.")
    except Exception as e:
        print(f"[DEBUG] Offline AI Warmup Error: {e}")
        speak("Warning. Offline AI failed to load.")

def local_llm_query(prompt, system_prompt="You are Jarvis. Answer strictly in one short sentence. Do not elaborate.", model="tinyllama", temp=0.2, max_tokens=100):
    """Queries your local offline LLM via Ollama with strict output limiters."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": temp,           # 0.1 = robotic/precise, 0.8 = creative/rambling
            "num_predict": max_tokens      # Hard cap on how many words it can generate
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json()['response'].strip()
    except requests.exceptions.ConnectionError:
        return "ERROR_OFFLINE: Ollama server is not running."
    except Exception as e:
        return f"Offline AI error: {e}"

def determine_intent(user_input):
    """Uses the tiny local LLM to classify the user's intent instantly."""
    router_prompt = f"""
    Classify the following user input into exactly one of these two categories:
    1. COMMAND (if the user wants to open an app, control the volume, or perform a PC action)
    2. QUESTION (if the user is asking for information, code generation, or general knowledge)
    
    Respond ONLY with the word COMMAND or QUESTION.
    User input: "{user_input}"
    """
    # Extremely low temperature and token limit for lightning-fast routing
    intent = local_llm_query(
        router_prompt, 
        system_prompt="You are a strict text classification engine. Output exactly one word.", 
        model="tinyllama", 
        temp=0.0, 
        max_tokens=5
    )
    if "COMMAND" in intent.upper():
        return "COMMAND"
    return "QUESTION"

def generate_and_open_code(prompt):
    """Generates pure code using the local LLM and safely opens it in VS Code."""
    speak("Generating code offline. Please wait a moment, sir.")
    
    code_prompt = f"Request: {prompt}"
    
    # Strict prompt forcing it to act like a compiler, not a chatbot
    strict_coder_prompt = "You are a Python compiler. Output ONLY raw, runnable Python code. NO markdown formatting. NO backticks. NO explanations. NO comments."
    
    generated_code = local_llm_query(
        code_prompt, 
        system_prompt=strict_coder_prompt, 
        model="tinyllama", 
        temp=0.1,         # Keeps code predictable and syntax-perfect
        max_tokens=400    # Allows enough room for the code snippet
    )
    
    if "ERROR_OFFLINE" in generated_code:
        speak("My offline AI engine is currently unreachable. Please ensure Ollama is running.")
        return

    # Extra safety cleanup in case TinyLlama disobeys the prompt
    generated_code = generated_code.replace("```python", "").replace("```", "").strip()
    
    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "jarvis_generated.py")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(generated_code)
    
    speak("Code generated. Opening in Visual Studio Code for your review.")
    
    try:
        subprocess.run(["code", file_path], shell=True)
    except Exception:
        speak("I could not find VS Code in your system path. Opening in Notepad instead.")
        os.system(f"start notepad {file_path}")

# ==========================================
# MAIN JARVIS LOOP
# ==========================================
def jarvis_main():
    speak("Jarvis online and ready.")
    
    start_listening_thread()
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

            elif "launch" in command and "open" not in command:
                app_name = command.replace("launch", "").strip()
                if app_name:
                    speak(f"Attempting to launch {app_name}")
                    success = open_windows_app(app_name)
                    if not success:
                        speak(f"Could not find or launch application {app_name}.")
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
                import re
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
                    news_api = NEWSAPI_KEY 
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
                    
             # --- ADVANCED OS COMMANDS ---
            elif "type for me" in command:
                speak("What should I type, sir?")
                dictation = listen() 
                if dictation:
                    type_dictation(dictation)
                    speak("Typing complete.")

            elif "switch window" in command or "switch tab" in command:
                speak("Switching window.")
                window_control("switch")

            elif "close this window" in command or "close app" in command:
                speak("Closing current application.")
                window_control("close")

            elif "minimize all" in command or "show desktop" in command:
                speak("Minimizing all windows.")
                window_control("minimize all")

            elif "read clipboard" in command or "what did i copy" in command:
                response = read_clipboard()
                speak(response)

            elif "empty recycle bin" in command or "empty trash" in command:
                response = empty_recycle_bin()
                speak(response)

            elif "clear temp files" in command or "optimize system" in command:
                speak("Initiating system optimization...")
                response = clear_temp_files()
                speak(response)

            elif "open" in command:
                app_name = command.replace("open", "").strip()
                if app_name:
                    response = dynamic_app_launcher(app_name)
                    speak(response)          

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

            # === OFFLINE AI FALLBACK (Code Generation & Questions) ===
            else:
                intent = determine_intent(command)
                
                if intent == "QUESTION":
                    if any(kw in command for kw in ["write code", "generate code", "code for", "python script"]):
                        threading.Thread(target=generate_and_open_code, args=(command,), daemon=True).start()
                    else:
                        def offline_answer(query):
                            # Check if the user explicitly asked for an explanation
                            if "explain" in query.lower():
                                system_prompt = "You are Jarvis. Provide a clear, detailed, and helpful explanation for the user's query."
                                # Higher tokens and temp for a detailed answer
                                answer = local_llm_query(query, system_prompt=system_prompt, temp=0.4, max_tokens=300)
                            else:
                                system_prompt = "You are Jarvis. Answer strictly in one short, direct sentence. Give the answer immediately. No yapping. No elaborating."
                                # Extremely strict limits for a 1-line answer
                                answer = local_llm_query(query, system_prompt=system_prompt, temp=0.1, max_tokens=40)
                            
                            if "ERROR_OFFLINE" in answer:
                                speak("My offline AI engine is unreachable.")
                            else:
                                speak(answer)
                                
                        threading.Thread(target=offline_answer, args=(command,), daemon=True).start()
                else:
                    pass

        except Exception as e:
            handle_error("jarvis_main", e)