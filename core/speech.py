import win32com.client
import pythoncom
import speech_recognition as sr
import queue
import threading
import time

from core.config import WAKE_WORD

# A Lock ensures Jarvis doesn't try to listen and speak at the exact same micro-second
audio_lock = threading.Lock()
speech_queue = queue.Queue()
is_speaking_flag = False
stop_speaking_event = threading.Event()

def _speech_worker():
    global is_speaking_flag
    """Handles the TTS engine in a dedicated thread."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass
        
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 0 # -10 to 10 range
        speaker.Volume = 100

        # Set Zira Voice
        for voice in speaker.GetVoices():
            if "zira" in voice.GetDescription().lower():
                speaker.Voice = voice
                break
    except Exception as e:
        print(f"[TTS Init Error] {e}")
        return

    SVSFlagsAsync = 1
    SVSFPurgeBeforeSpeak = 2

    while True:
        item = speech_queue.get()
        if item is None: break
        
        text, event = item
        
        try:
            # We explicitly do NOT use audio_lock here so _listen_loop can run simultaneously
            stop_speaking_event.clear()
            is_speaking_flag = True
            speaker.Speak(text, SVSFlagsAsync)
            
            while True:
                if speaker.WaitUntilDone(100):
                    break
                if stop_speaking_event.is_set():
                    speaker.Speak("", SVSFPurgeBeforeSpeak | SVSFlagsAsync)
                    break
        except Exception as e:
            print(f"[Speak Error] {e}")
        finally:
            is_speaking_flag = False
            if event:
                event.set()
            speech_queue.task_done()

# Start speech worker
threading.Thread(target=_speech_worker, daemon=True).start()

def speak(text, wait=True):
    """Sends text to the speech queue and optionally waits for it to finish."""
    print(f"JARVIS: {text}")
    event = threading.Event() if wait else None
    speech_queue.put((text, event))
    
    if wait:
        event.wait()

REQUIRE_WAKE_WORD = True

# --- Flawless Speech Recognition Setup ---
r = sr.Recognizer()

# CORE OPTIMIZATIONS
r.energy_threshold = 300 
r.dynamic_energy_threshold = True 
r.dynamic_energy_adjustment_damping = 0.15 
r.dynamic_energy_ratio = 1.5

r.pause_threshold = 1.2
r.non_speaking_duration = 0.5
r.operation_timeout = None

command_queue = queue.Queue()
listening_thread_active = False

def _listen_loop():
    """Background thread that continuously listens for speech without freezing."""
    global listening_thread_active
    
    with sr.Microphone() as source:
        print("\n🎙️ Initializing microphone and mapping ambient noise...")
        r.adjust_for_ambient_noise(source, duration=2.0)
        print("✅ Microphone calibrated. Jarvis is now listening flawlessly.")
        
        while listening_thread_active:
            try:
                # No audio_lock here: we listen concurrently to allow interruptions
                audio = r.listen(source, timeout=1, phrase_time_limit=20)
                
                threading.Thread(target=_process_audio, args=(audio,), daemon=True).start()
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"[Mic Error] {e}")
                time.sleep(1)

def _process_audio(audio):
    """Sends captured audio to the transcription engine."""
    global REQUIRE_WAKE_WORD, is_speaking_flag
    try:
        command = r.recognize_google(audio).lower()
        
        # If Jarvis is currently speaking, ONLY accept interrupt commands to avoid self-triggering feedback loops
        if is_speaking_flag:
            if any(word in command for word in ["stop", "wait"]):
                print("🛑 Interrupting Jarvis...")
                stop_speaking_event.set()
                # Empty the speech queue so he doesn't immediately say the next queued sentence
                while not speech_queue.empty():
                    try:
                        item = speech_queue.get_nowait()
                        if item[1]:
                            item[1].set()
                        speech_queue.task_done()
                    except queue.Empty:
                        break
            return # Ignore all other transcribed words while Jarvis is speaking
        
        if REQUIRE_WAKE_WORD:
            if WAKE_WORD in command:
                cleaned_command = command.replace(WAKE_WORD, "").strip()
                if cleaned_command: 
                    print(f"👤 You: {cleaned_command}")
                    command_queue.put(cleaned_command)
                else: 
                    speak("Sir?")
        else:
            print(f"👤 You: {command}")
            command_queue.put(command)
            
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print("⚠️ [Network Error] Could not connect to Speech Recognition servers.")

def start_listening_thread():
    """Starts the background listening loop."""
    global listening_thread_active
    if not listening_thread_active:
        listening_thread_active = True
        t = threading.Thread(target=_listen_loop, daemon=True)
        t.start()

def stop_listening_thread():
    """Stops the background listening loop."""
    global listening_thread_active
    listening_thread_active = False

def get_next_command(timeout=1.0):
    """Retrieves the next recognized command from the queue."""
    try:
        return command_queue.get(timeout=timeout)
    except queue.Empty:
        return None

def listen():
    """Direct, synchronous listen function used specifically for dictation."""
    with sr.Microphone() as source:
        try:
            with audio_lock:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("🎧 Dictation active...")
                audio = r.listen(source, timeout=5, phrase_time_limit=20)
            return r.recognize_google(audio).lower()
        except:
            return ""