import pyttsx3
import speech_recognition as sr
import os
import threading

import queue

tts_queue = queue.Queue()

def tts_worker():
    # Keep initialization in the thread so that COM doesn't crash
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception:
        pass
        
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # Set the speech rate (default is 0, range is generally -10 to +10)
    speaker.Rate = 1
    
    while True:
        item = tts_queue.get()
        if item is None:
            break
        text, event = item
        try:
            speaker.Speak(text)
        except Exception as e:
            print(f"[Speak Error] {e}")
        finally:
            if event:
                event.set()
            tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    print(f"JARVIS: {text}")
    event = threading.Event()
    tts_queue.put((text, event))
    event.wait()  # Block caller until speech finishes to prevent overlapping audio

def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = r.listen(source)
            recog_result = r.recognize_google(audio)
            if isinstance(recog_result, str):
                return recog_result.lower()
            elif isinstance(recog_result, (list, tuple)):
                for alt in recog_result:
                    if isinstance(alt, str):
                        return alt.lower()
                print("[ERROR] No valid string recognized in alternatives.")
                return ""
            else:
                print(f"[ERROR] Unexpected recognition result type: {type(recog_result)}")
                return ""
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        speak("I'm having trouble connecting to the speech service.")
        return ""
    except Exception as e:
        from core.utils import handle_error
        handle_error("listen", e)
        return ""

import queue

command_queue = queue.Queue()
listening_thread = None
stop_event = threading.Event()
REQUIRE_WAKE_WORD = True  # Flag to allow real-time continuous conversation

def background_listen_loop(wake_word="jarvis"):
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5  # Fast response time (0.5s of silence marks end of phrase)
    
    print(f"[STANDBY] Continuous listening for '{wake_word}' in background...")
    
    while not stop_event.is_set():
        try:
            with sr.Microphone() as source:
                print("[STANDBY] Calibrating microphone for background noise...")
                r.adjust_for_ambient_noise(source, duration=1.5)
                print("[STANDBY] Microphone active and real-time.")
                
                while not stop_event.is_set():
                    try:
                        # timeout=1 to allow checking stop_event frequently
                        audio = r.listen(source, timeout=1, phrase_time_limit=10)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception:
                        continue
                    
                    try:
                        text = r.recognize_google(audio)
                        if not isinstance(text, str):
                            if isinstance(text, (list, tuple)):
                                text = next((a for a in text if isinstance(a, str)), "")
                            else:
                                text = ""
                        text = text.lower().strip()
                    except sr.UnknownValueError:
                        continue # Background noise ignored silently
                    except sr.RequestError:
                        continue
                    except Exception:
                        continue
                    
                    if not text:
                        continue
                        
                    global REQUIRE_WAKE_WORD
                    if not REQUIRE_WAKE_WORD:
                        print(f"👤 [Voice]: {text}")
                        command_queue.put(text)
                    elif wake_word in text:
                        command = text.split(wake_word, 1)[-1].strip()
                        if command:
                            print(f"👤 Command explicitly triggered: {command}")
                            command_queue.put(command)
                        else:
                            import winsound
                            winsound.Beep(500, 200)  # Gentle beep to indicate Jarvis is listening
                            try:
                                cmd_audio = r.listen(source, timeout=3, phrase_time_limit=10)
                                command = r.recognize_google(cmd_audio)
                                if isinstance(command, str) and command:
                                    print(f"👤 Command: {command}")
                                    command_queue.put(command.lower())
                            except (sr.UnknownValueError, sr.WaitTimeoutError):
                                continue
        except Exception as e:
            from core.utils import handle_error
            handle_error("background_listen_loop", e)
            import time
            time.sleep(1)

def start_listening_thread():
    global listening_thread
    if listening_thread is None or not listening_thread.is_alive():
        stop_event.clear()
        listening_thread = threading.Thread(target=background_listen_loop, daemon=True)
        listening_thread.start()

def stop_listening_thread():
    stop_event.set()

def get_next_command(timeout=1.0):
    try:
        return command_queue.get(timeout=timeout)
    except queue.Empty:
        return None
