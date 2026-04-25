import sys
from core.speech import speak  # Assuming speak is imported from core.speech

def global_scope():
    """
    This function handles the graceful shutdown of JARVIS when a KeyboardInterrupt occurs.
    It attempts to speak a shutdown message, but robustly handles the case where
    the speech itself might be interrupted by a second KeyboardInterrupt during cleanup.
    """
    try:
        # Attempt to speak the shutdown message.
        # The original traceback showed a second KeyboardInterrupt occurring here,
        # because speak's internal threading.Event.wait() was interrupted.
        speak("Manual override engaged. JARVIS shutting down.")
    except KeyboardInterrupt:
        # If speak is also interrupted during the cleanup phase (e.g., user presses Ctrl+C repeatedly),
        # catch this secondary interrupt to prevent another unhandled exception.
        # Fallback to printing the message directly to stderr.
        print("\nJARVIS shutdown sequence interrupted during speech.", file=sys.stderr)
    except Exception as e:
        # Catch any other unexpected errors that might occur during the shutdown speech attempt.
        print(f"\nError during JARVIS shutdown speech: {e}", file=sys.stderr)
    finally:
        # Add any other critical cleanup actions here that must run regardless
        # of whether speech succeeded or was interrupted.
        # These actions should also be designed to be as robust and non-blocking as possible
        # during an emergency shutdown.
        pass