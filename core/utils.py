# core/utils.py
import traceback
import sys
import requests
from core.speech import speak

def ask_tinyllama_debug(prompt):
    """Queries the local offline AI for debugging."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "system": "You are a strict Python debugging assistant. Output ONLY the code fix or a single sentence explanation. No yapping.",
        "stream": False,
        "options": {
            "temperature": 0.1,  # Keeps it highly analytical and robotic
            "num_predict": 150   # Prevents it from rambling
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['response'].strip()
    except Exception:
        return "[Error: Local AI is offline or unreachable]"

def handle_error(func_name, exception_obj):
    """Catches errors and asks TinyLlama for a fix."""
    error_msg = ''.join(traceback.format_exception(None, exception_obj, exception_obj.__traceback__))
    print(f"\n[CRITICAL ERROR in {func_name}] {error_msg}")
    speak("Error detected. Attempting to self heal offline.")
    
    try:
        fix_prompt = f"Identify and fix this Python error in function {func_name}:\n{error_msg}"
        repaired_code = ask_tinyllama_debug(fix_prompt)
        
        print(f"\n[TinyLlama Debug Suggestion]:\n{repaired_code}\n")
        speak("A potential fix has been suggested by my offline network. Please review the terminal.")
        
    except Exception as repair_error:
        print(f"[Offline Auto-Repair Failed] {repair_error}")
        speak("Self healing protocol failed.")

def setup_global_exception_hook():
    """Catches any errors that happen completely outside of Jarvis's main loop."""
    def custom_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        handle_error("Uncaught Exception", exc_value)
    sys.excepthook = custom_excepthook