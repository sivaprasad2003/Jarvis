import json
import os
import datetime
from core.speech import speak

MEMORY_FILE = "memory.json"

def remember_this(fact):
    memory = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                memory = json.load(f)
        except:
            pass
            
    memory.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "fact": fact
    })
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
        
    speak("Got it. I will remember that.")

def recall_memory():
    if not os.path.exists(MEMORY_FILE):
        speak("I don't have any memory stored yet.")
        return
        
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
            
        if memory:
            speak(f"I remember {len(memory)} things.")
            for item in memory:
                speak(item["fact"])
        else:
            speak("I don't have anything stored.")
    except Exception as e:
        speak("My memory file seems corrupted.")
