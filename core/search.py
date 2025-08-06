# core/search_commands.py
import webbrowser
from core.speech import speak

def handle_search(command):
    if "search google for" in command:
        query = command.replace("search google for", "").strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching Google for {query}.")
        else:
            speak("Please specify what to search for on Google.")

    elif "search amazon for" in command:
        query = command.replace("search amazon for", "").strip()
        if query:
            url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching Amazon for {query}.")
        else:
            speak("Please specify what to search for on Amazon.")

    elif "search flipkart for" in command:
        query = command.replace("search flipkart for", "").strip()
        if query:
            url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching Flipkart for {query}.")
        else:
            speak("Please specify what to search for on Flipkart.")
