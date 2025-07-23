# core/gui.py
import customtkinter as ctk
from core.speech import speak
from threading import Thread
from core.shared_utils import jarvis_main

def run_jarvis():
    speak("Starting JARVIS Assistant.")
    jarvis_main()

def launch_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("JARVIS Assistant")
    app.geometry("400x300")

    label = ctk.CTkLabel(app, text="Welcome to JARVIS", font=("Roboto", 22))
    label.pack(pady=20)

    start_btn = ctk.CTkButton(app, text="Start Assistant", command=lambda: Thread(target=run_jarvis).start())
    start_btn.pack(pady=10)

    exit_btn = ctk.CTkButton(app, text="Exit", command=app.destroy)
    exit_btn.pack(pady=10)

    app.mainloop()


