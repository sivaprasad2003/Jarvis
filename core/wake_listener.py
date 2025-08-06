# core/wake_listener.py
import speech_recognition as sr
import sys

WAKE_WORD = "jarvis"

def passive_listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=2)
            print("🎧 Jarvis is in standby mode. Say 'Jarvis' followed by your command.")
            while True:
                try:
                    print("🔔 Please speak now...")
                    audio = recognizer.listen(mic, phrase_time_limit=5)
                    audio_duration = len(audio.frame_data) / audio.sample_rate
                    print(f"[DEBUG] Audio captured, duration: {audio_duration:.2f} seconds")
                    try:
                        result = recognizer.recognize_google(audio)
                        print("[DEBUG] Google recognizer used.")
                    except sr.UnknownValueError:
                        print("❓ Google could not understand audio. Trying Sphinx...")
                        try:
                            result = recognizer.recognize_sphinx(audio)
                            print("[DEBUG] Sphinx recognizer used.")
                        except sr.UnknownValueError:
                            print("❓ Sphinx could not understand audio. Retrying...")
                            continue
                        except Exception as sphinx_e:
                            print(f"[ERROR] Sphinx error: {sphinx_e}. Retrying...")
                            continue
                    except sr.RequestError as e:
                        print(f"[ERROR] Could not request results from Google speech service: {e}. Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
                        continue
                    except Exception as google_e:
                        print(f"[Unexpected Google Error] {google_e}. Retrying...")
                        continue
                    if isinstance(result, str):
                        query = result.lower()
                    else:
                        print(f"[ERROR] Unexpected recognition result type: {type(result)}")
                        continue
                    print(f"[Recognized]: {query}")
                    if query.startswith(WAKE_WORD):
                        command = query.replace(WAKE_WORD, "", 1).strip()
                        if "exit" in command:
                            print("👋 Exit command received. Shutting down Jarvis.")
                            sys.exit()
                        return command  # ✅ Forward to main processing
                    else:
                        print(f"⏳ Wake word not detected in: '{query}'. Still listening...")
                except Exception as e:
                    print(f"[Unexpected Error] {e}. Retrying...")
    except Exception as outer_e:
        print(f"[CRITICAL] Microphone or recognizer error: {outer_e}")