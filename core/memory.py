# core/memory.py
from core.speech import speak

MEMORY_FILE = "memory.txt"

def remember_this(fact):
    with open(MEMORY_FILE, "a") as f:
        f.write(fact + "\n")
    speak("Got it. I will remember that.")

def recall_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                speak("Here is what I remember:")
                for line in lines:
                    speak(line.strip())
            else:
                speak("I don't have anything stored.")
    except FileNotFoundError:
        speak("I don't have any memory stored yet.")
