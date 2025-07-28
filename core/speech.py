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

def listen(timeout=5, retries=2, wake_word="jarvis"):
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
                    if wake_word in text:
                        speak("I'm here, sir.")
                        return ""
            except sr.WaitTimeoutError:
                print("🕓 Still waiting for wake word...")
            except Exception as e:
                from core.utils import handle_error
                handle_error("wake_word_listen", e)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you repeat?")
        except sr.RequestError:
            speak("I'm having trouble connecting to the speech service.")
        except Exception as e:
            from core.utils import handle_error
            handle_error("listen", e)
    return ""
