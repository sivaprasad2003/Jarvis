import pyttsx3
import speech_recognition as sr
import os
import threading

engine = pyttsx3.init()
lock = threading.Lock()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    print(f"JARVIS: {text}")
    with lock:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[Speak Error] {e}")

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

def standby_mode(on_wake_callback=None, wake_word="jarvis"):
    r = sr.Recognizer()
    print(f"[STANDBY] Continuous listening for wake word '{wake_word}'...")
    while True:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source)
                try:
                    recog_result = r.recognize_google(audio)
                    if isinstance(recog_result, str):
                        text = recog_result.lower()
                    elif isinstance(recog_result, (list, tuple)):
                        text = ""
                        for alt in recog_result:
                            if isinstance(alt, str):
                                text = alt.lower()
                                break
                    else:
                        text = ""
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    speak("I'm having trouble connecting to the speech service.")
                    continue
                if wake_word in text:
                    # Extract command after wake word
                    command = text.split(wake_word, 1)[-1].strip()
                    if command:
                        print(f"👤 Command after wake word: {command}")
                        return command
                    else:
                        speak("I'm here, sir. Listening for your command...")
                        while True:
                            try:
                                with sr.Microphone() as cmd_source:
                                    r.adjust_for_ambient_noise(cmd_source, duration=1)
                                    print("🎧 Listening for your command...")
                                    cmd_audio = r.listen(cmd_source)
                                    command = r.recognize_google(cmd_audio)
                                    print(f"👤 You said: {command}")
                                    return command.lower() if isinstance(command, str) else ""
                            except sr.UnknownValueError:
                                continue
                            except Exception as e:
                                from core.utils import handle_error
                                handle_error("standby_mode_command", e)
                                continue
        except Exception as e:
            from core.utils import handle_error
            handle_error("standby_mode", e)
            continue
