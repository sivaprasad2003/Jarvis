import face_recognition
import cv2
import speech_recognition as sr
import pyttsx3
import cvlib as cv
from cvlib.object_detection import draw_bbox
import google.generativeai as genai
import traceback
import time
import sys
import os
import psutil
import datetime
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ========== CONFIG ==========
GEMINI_API_KEY = "AIzaSyDAJfovc7LPw8cr6bzaz7fxME3N5bINX70"  # Replace with your Gemini API Key
WAKE_WORD = "jarvis"
MEMORY_STORE = ""
STANDBY_MODE = False
AI_MODE = False

# ========== Setup ==========
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
genai.configure(api_key=GEMINI_API_KEY)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

def speak(text):
    print(f"JARVIS: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Speak Error] {e}")

def listen(timeout=5, retries=2):
    r = sr.Recognizer()
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                print("🎙️ Adjusting for ambient noise...")
                r.adjust_for_ambient_noise(source, duration=1.0)
                print("🎧 Listening for your command...")
                audio = r.listen(source, timeout=timeout)
                command = r.recognize_google(audio)
                print(f"👤 You said: {command}")
                return command.lower()
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected.")
            speak("Please speak or say 'Jarvis' to activate me.")
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1.0)
                    print("🎧 Listening for wake word...")
                    audio = r.listen(source, timeout=10)
                    text = r.recognize_google(audio).lower()
                    if WAKE_WORD in text:
                        speak("I'm here, sir.")
                        return ""
            except sr.WaitTimeoutError:
                print("🕓 Still waiting for wake word...")
            except Exception as e:
                handle_error("wake_word_listen", e)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you repeat?")
        except sr.RequestError:
            speak("I'm having trouble connecting to the speech service.")
        except Exception as e:
            handle_error("listen", e)
    return ""

def standby_loop():
    global STANDBY_MODE
    r = sr.Recognizer()
    speak("Entering standby mode. Say 'Jarvis' to reactivate.")
    while STANDBY_MODE:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.8)
                print("🔇 Standby: Listening for wake word...")
                audio = r.listen(source, timeout=10)
                result = r.recognize_google(audio).lower()
                print(f"🗣️ Detected: {result}")
                if WAKE_WORD in result:
                    speak("System reactivated, sir. How may I assist you?")
                    STANDBY_MODE = False
                    return
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except Exception as e:
            handle_error("standby_loop", e)
            time.sleep(1)

def ask_gemini(prompt, model_name="gemini-1.5-flash", retries=2):
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini Error {model_name}] Attempt {attempt + 1}: {e}")
            if attempt == retries - 1:
                return f"[Gemini Error]: {e}"
            time.sleep(1)
    return "I'm sorry, I couldn't process that request."

def ask_gemini_fallback(prompt):
    response = ask_gemini(prompt, "gemini-1.5-flash")
    if "[Gemini Error]" in response:
        response = ask_gemini(prompt, "gemini-1.5-pro")
    return response

def welcome_greeting():
    hour = datetime.datetime.now().hour
    greetings = {
        (5, 12): "Good morning, sir. Ready to conquer the day?",
        (12, 17): "Good afternoon, sir. How's your day going?",
        (17, 22): "Good evening, sir. Time to unwind?",
        (22, 5): "Good night, sir. Burning the midnight oil?"
    }
    for (start, end), greeting in greetings.items():
        if start <= hour < end:
            speak(greeting)
            break
    battery = psutil.sensors_battery()
    if battery and battery.percent == 100 and battery.power_plugged:
        speak("Battery is fully charged. Consider unplugging to preserve battery health.")

def handle_error(func_name, exception_obj):
    error_msg = ''.join(traceback.format_exception(None, exception_obj, exception_obj.__traceback__))
    print(f"[CRITICAL ERROR in {func_name}] {error_msg}")
    speak(f"Error detected in {func_name}. Attempting to diagnose...")
    try:
        fix_prompt = f"Fix this Python error in function {func_name}:\n{error_msg}"
        repaired_code = ask_gemini_fallback(fix_prompt)
        print(f"[Gemini Debug Suggestion]:\n{repaired_code}")
        speak("A potential fix has been suggested. Manual review recommended.")
    except Exception as repair_error:
        print(f"[Auto-Repair Failed] {repair_error}")
        speak("Repair attempt failed. Please check the logs.")

def load_known_faces():
    known_encodings = []
    known_names = []
    try:
        if not os.path.exists("authorized_faces"):
            os.makedirs("authorized_faces")
        for filename in os.listdir("authorized_faces"):
            if filename.endswith((".jpg", ".png")):
                image = face_recognition.load_image_file(f"authorized_faces/{filename}")
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    known_encodings.append(encoding[0])
                    known_names.append(os.path.splitext(filename)[0])
        return known_encodings, known_names
    except Exception as e:
        handle_error("load_known_faces", e)
        return [], []

def face_login():
    try:
        known_encodings, known_names = load_known_faces()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera initialization failed.")
            return False
        speak("Initiating facial authentication.")
        attempts = 0
        while attempts < 3:
            ret, frame = cap.read()
            if not ret:
                speak("Camera feed error.")
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
            if rgb.dtype != np.uint8:
                rgb = rgb.astype(np.uint8)
            if not rgb.flags['C_CONTIGUOUS']:
                rgb = np.ascontiguousarray(rgb)
            print(f"[DEBUG] Image dtype: {rgb.dtype}, shape: {rgb.shape}, contiguous: {rgb.flags['C_CONTIGUOUS']}")
            faces = face_recognition.face_encodings(rgb)
            if faces:
                match_results = face_recognition.compare_faces(known_encodings, faces[0])
                if True in match_results:
                    index = match_results.index(True)
                    name = known_names[index]
                    speak(f"Access granted, {name}. Systems online.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    speak("Access denied. Unauthorized face detected.")
                    attempts += 1
            else:
                speak("No face detected. Please align your face with the camera.")
            cv2.putText(frame, f"Attempts: {attempts}/3 - Press 'A' to enroll", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.imshow("Facial Login - Q to quit", frame)
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                speak("Authentication cancelled.")
                break
            elif key == ord('a'):
                speak("Initiating new face enrollment.")
                cap.release()
                cv2.destroyAllWindows()
                add_face()
                return face_login()
        speak("Three failed attempts. Register new face? Say 'yes' or 'no'.")
        for _2 in range(2):
            response = listen().lower()
            if "yes" in response:
                cap.release()
                cv2.destroyAllWindows()
                add_face()
                return face_login()
            elif "no" in response:
                break
        cap.release()
        cv2.destroyAllWindows()
        speak("Access denied. System locked.")
        sys.exit()
    except Exception as e:
        handle_error("face_login", e)
        cap.release()
        cv2.destroyAllWindows()
        return False

def add_face():
    try:
        speak("Please state your name for identification.")
        name = listen().lower().replace(" ", "_")
        if not name:
            speak("Name not recognized. Enrollment cancelled.")
            return
        speak(f"Capturing face for {name} in 3 seconds.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera initialization failed.")
            return
        time.sleep(3)
        ret, frame = cap.read()
        if not ret:
            speak("Failed to capture image.")
            cap.release()
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
        if rgb.dtype != np.uint8:
           rgb = rgb.astype(np.uint8)
        if not rgb.flags['C_CONTIGUOUS']:
           rgb = np.ascontiguousarray(rgb)
        print(f"[DEBUG] Image dtype: {rgb.dtype}, shape: {rgb.shape}, contiguous: {rgb.flags['C_CONTIGUOUS']}")
        faces = face_recognition.face_encodings(rgb)
        if faces:
            if not os.path.exists("authorized_faces"):
                os.makedirs("authorized_faces")
            cv2.imwrite(f"authorized_faces/{name}.jpg", frame)
            speak(f"Identity {name} registered successfully.")
        else:
            speak("No face detected. Please try again.")
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        handle_error("add_face", e)
        if 'cap' in locals():
            cap.release()
            cv2.destroyAllWindows()

def detect_objects():
    try:
        import numpy as np
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera initialization failed. Please check your camera connection.")
            return
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        speak("Object recognition engaged. Say 'what do you see', 'what is this', 'is there a [object]', or 'stop' to exit.")

        trackers = cv2.legacy.MultiTracker_create()
        detected_objects = {}
        last_spoken = set()
        last_detection_time = time.time()
        tracker_initialized = False

        while True:
            ret, frame = cap.read()
            if not ret:
                speak("Camera feed lost. Terminating object detection.")
                break
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)

            if tracker_initialized:
                success, boxes = trackers.update(frame)
                temp_objects = {}
                for i, box in enumerate(boxes):
                    label = list(detected_objects.keys())[i % len(detected_objects)]
                    temp_objects[label] = temp_objects.get(label, 0) + 1
                    x, y, w, h = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} ({temp_objects[label]})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                detected_objects = temp_objects

            current_time = time.time()
            if current_time - last_detection_time > 2.0 or not tracker_initialized:
                bbox, label, conf = cv.detect_common_objects(frame, confidence=0.6, nms_thresh=0.4)
                detected_objects = {}
                for l in label:
                    detected_objects[l] = detected_objects.get(l, 0) + 1
                trackers = cv2.legacy.MultiTracker_create()
                for box in bbox:
                    tracker = cv2.legacy.TrackerCSRT_create()
                    trackers.add(tracker, frame, tuple(box))
                tracker_initialized = True
                last_detection_time = current_time

                if detected_objects and set(detected_objects.keys()) != last_spoken:
                    object_counts = [f"{count} {label}" + ("s" if count > 1 else "") for label, count in detected_objects.items()]
                    label_str = " and ".join(object_counts)
                    speak(f"I see: {label_str}")
                    last_spoken = set(detected_objects.keys())

            for i, (label, count) in enumerate(detected_objects.items()):
                if i < len(bbox):
                    x, y, w, h = bbox[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} ({count})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Object Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                speak("Object detection terminated.")
                break

            spoken = listen(timeout=2)
            if 'stop' in spoken:
                speak("Object detection disengaged.")
                break
            elif 'what do you see' in spoken or 'what is this' in spoken:
                if detected_objects:
                    object_counts = [f"{count} {label}" + ("s" if count > 1 else "") for label, count in detected_objects.items()]
                    description = " and ".join(object_counts)
                    speak(f"I see: {description}")
                else:
                    speak("No objects detected at the moment.")
            elif 'is there a' in spoken or 'do you see a' in spoken:
                query = spoken.replace('is there a', '').replace('do you see a', '').strip()
                query = query.rstrip('?').strip()
                found = False
                for label, count in detected_objects.items():
                    if query in label.lower():
                        speak(f"Yes, I see {count} {label}" + ("s" if count > 1 else "") + ".")
                        found = True
                        break
                if not found:
                    speak(f"No {query} detected in the frame.")

        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        handle_error("detect_objects", e)
        speak("An error occurred during object detection.")
        if 'cap' in locals():
            cap.release()
            cv2.destroyAllWindows()

def increase_volume():
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.1, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume increased.")
    except Exception as e:
        handle_error("increase_volume", e)
        speak("Failed to adjust volume.")

def decrease_volume():
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.1, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume decreased.")
    except Exception as e:
        handle_error("decrease_volume", e)
        speak("Failed to adjust volume.")

def mute_volume():
    try:
        volume.SetMute(1, None)
        speak("System muted.")
    except Exception as e:
        handle_error("mute_volume", e)
        speak("Failed to mute system.")

def unmute_volume():
    try:
        volume.SetMute(0, None)
        speak("System unmuted.")
    except Exception as e:
        handle_error("unmute_volume", e)
        speak("Failed to unmute system.")

def get_weather():
    speak("Please specify the city for the weather report.")
    city = listen(timeout=10)
    if not city:
        speak("City not recognized.")
        return
    prompt = f"Current weather in {city}"
    response = ask_gemini_fallback(prompt)
    speak(response)

def take_screenshot():
    try:
        from PIL import Image
        import pyautogui
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot = pyautogui.screenshot()
        if not isinstance(screenshot, Image.Image):
            screenshot = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        screenshot_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{timestamp}.png")
        screenshot.save(screenshot_path)
        speak(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        handle_error("take_screenshot", e)
        speak("Failed to capture screenshot.")

def system_info():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        speak(f"System status: CPU at {cpu} percent, RAM at {ram} percent, Disk at {disk} percent.")
    except Exception as e:
        handle_error("system_info", e)
        speak("Failed to retrieve system information.")

def jarvis_main():
    global STANDBY_MODE, AI_MODE, MEMORY_STORE
    speak("JARVIS online. How may I serve you, sir?")
    while True:
        command = listen()
        if not command:
            continue
        print(f"YOU: {command}")
        if STANDBY_MODE:
            standby_loop()
            continue
        if "activate ai" in command:
            AI_MODE = True
            speak("Gemini AI mode engaged. Ask me anything, sir.")
            continue
        elif "deactivate ai" in command:
            AI_MODE = False
            speak("AI mode disengaged. Standard protocols resumed.")
            continue
        elif "object detection" in command or "detect objects" in command:
            detect_objects()
        elif "time" in command:
            now = time.strftime("%I:%M %p")
            speak(f"The current time is {now}.")
        elif "date" in command:
            today = datetime.date.today().strftime("%B %d, %Y")
            speak(f"Today's date is {today}.")
        elif "exit" in command or "shutdown jarvis" in command:
            speak("Shutting down JARVIS. Goodbye, sir.")
            break
        elif "open youtube" in command:
            speak("Launching YouTube.")
            os.system("start https://www.youtube.com")
        elif "open google" in command:
            speak("Opening Google.")
            os.system("start https://www.google.com")
        elif "open downloads" in command:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            speak("Accessing Downloads folder.")
            os.startfile(downloads_path)
        elif "play music" in command:
            music_folder = os.path.join(os.path.expanduser("~"), "Music")
            try:
                files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
                if files:
                    os.startfile(os.path.join(music_folder, files[0]))
                    speak("Playing music.")
                else:
                    speak("No music files found in your Music folder.")
            except Exception as e:
                handle_error("play_music", e)
                speak("Failed to play music.")
        elif "battery" in command:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not charging"
                speak(f"Battery at {percent} percent, {plugged}.")
            else:
                speak("Battery information unavailable.")
        elif "system status" in command or "system info" in command:
            system_info()
        elif "remember this" in command:
            MEMORY_STORE = command.replace("remember this", "").strip()
            speak(f"Stored in memory: {MEMORY_STORE}")
        elif "what did i tell you" in command or "do you remember" in command:
            if MEMORY_STORE:
                speak(f"You told me: {MEMORY_STORE}")
            else:
                speak("Memory banks empty, sir.")
        elif "remind me to" in command:
            reminder = command.replace("remind me to", "").strip()
            speak(f"Reminder set for: {reminder}. Note: I'm not a real reminder system yet!")
        elif "increase volume" in command:
            increase_volume()
        elif "decrease volume" in command:
            decrease_volume()
        elif "mute" in command:
            mute_volume()
        elif "unmute" in command:
            unmute_volume()
        elif "standby" in command or "stand by" in command:
            STANDBY_MODE = True
            continue
        elif "dark mode" in command:
            try:
                os.system("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 0 /f")
                speak("Dark mode activated.")
            except Exception as e:
                handle_error("dark_mode", e)
        elif "light mode" in command:
            try:
                os.system("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 1 /f")
                speak("Light mode activated.")
            except Exception as e:
                handle_error("light_mode", e)
        elif "lock system" in command:
            speak("Locking system now.")
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif "shutdown system" in command or "power off" in command:
            speak("Initiating system shutdown.")
            os.system("shutdown /s /t 1")
        elif "restart system" in command or "reboot" in command:
            speak("Rebooting system.")
            os.system("shutdown /r /t 1")
        elif "hibernate system" in command:
            speak("Entering hibernation.")
            try:
                ctypes.windll.PowrProf.SetSuspendState(True, True, True)
            except Exception as e:
                handle_error("hibernate", e)
                speak("Hibernation failed.")
        elif "weather" in command:
            get_weather()
        elif "open notepad" in command:
            speak("Opening Notepad.")
            os.system("start notepad")
        elif "open calculator" in command:
            speak("Opening Calculator.")
            os.system("start calc")
        elif "take screenshot" in command:
            take_screenshot()
        elif AI_MODE and command.strip():
            response = ask_gemini_fallback(command)
            speak(response)
        elif command.strip():
            speak("Command not recognized. Perhaps try something else, sir?")
        time.sleep(0.5)

if __name__ == "__main__":
    speak("Initializing JARVIS core systems...")
    try:
        if face_login():
            welcome_greeting()
            jarvis_main()
    except KeyboardInterrupt:
        speak("Manual override detected. JARVIS shutting down.")
    except Exception as main_error:
        handle_error("main", main_error)