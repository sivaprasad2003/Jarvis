import traceback
import sys
import datetime
from core.speech import speak, stop_listening_thread
from core.gemini_ai import ask_gemini_fallback

def generate_and_save_patch(func_name, error_msg):
    try:
        fix_prompt = f"You are an expert Python developer. Fix this Python error in function {func_name}:\n{error_msg}\n\nReturn ONLY the valid python code block with the fixed function, no other text."
        repaired_code = ask_gemini_fallback(fix_prompt)
        
        # Clean up code blocks if they exist
        if repaired_code.startswith("```python"):
            repaired_code = repaired_code[9:]
        elif repaired_code.startswith("```"):
            repaired_code = repaired_code[3:]
        if repaired_code.endswith("```"):
            repaired_code = repaired_code[:-3]
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        patch_file = f"auto_patch_{func_name}_{timestamp}.py"
        with open(patch_file, "w") as f:
            f.write(repaired_code.strip())
        print(f"[Self-Healing] Proposed patch saved to {patch_file}")
        return patch_file
    except Exception as e:
        print(f"Failed to generate patch: {e}")
        return None

def handle_error(func_name, exception_obj):
    error_msg = ''.join(traceback.format_exception(None, exception_obj, exception_obj.__traceback__))
    print(f"[CRITICAL ERROR in {func_name}] {error_msg}")
    speak(f"Error detected in {func_name}. Attempting to self heal.")
    
    patch_file = generate_and_save_patch(func_name, error_msg)
    if patch_file:
        speak(f"A self-healing patch has been generated and saved to {patch_file}. Please review.")
    else:
        speak("Self healing attempt failed. Please check the logs.")

def global_exception_hook(exctype, value, tb):
    print("FATAL UNHANDLED EXCEPTION:", file=sys.stderr)
    traceback.print_exception(exctype, value, tb)
    
    try:
        from core.object_detection import stop_detection_event
        stop_detection_event.set()
        stop_listening_thread()
    except:
        pass
    
    speak("Fatal system failure detected. Initiating emergency shutdown protocols.")
    
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    generate_and_save_patch("global_scope", error_msg)
    
    sys.exit(1)

def setup_global_exception_hook():
    sys.excepthook = global_exception_hook

