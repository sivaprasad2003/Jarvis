import traceback
from core.speech import speak
from core.gemini_ai import ask_gemini_fallback

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
