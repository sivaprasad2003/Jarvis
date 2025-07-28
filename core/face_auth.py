import cv2
import numpy as np
import os
import sys
import face_recognition
from core.speech import speak, listen
from core.utils import handle_error

def load_known_faces():
    encodings, names = [], []
    try:
        os.makedirs("authorized_faces", exist_ok=True)
        for f in os.listdir("authorized_faces"):
            if f.endswith((".jpg", ".png")):
                image = face_recognition.load_image_file(f"authorized_faces/{f}")
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    encodings.append(encoding[0])
                    names.append(os.path.splitext(f)[0])
    except Exception as e:
        handle_error("load_known_faces", e)
    return encodings, names

def register_new_face():
    try:
        speak("Please state your name.")
        name = listen().strip().replace(" ", "_")
        if not name:
            speak("Name not recognized. Registration cancelled.")
            return
        cap = cv2.VideoCapture(0)
        speak(f"Capturing your face, {name}. Please hold still.")
        for _ in range(3):
            ret, frame = cap.read()
            if not ret:
                speak("Camera error during registration.")
                return
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_encodings(rgb)
            if faces:
                path = f"authorized_faces/{name}.jpg"
                cv2.imwrite(path, frame)
                speak(f"Face registered successfully as {name}.")
                speak(f"Let me introduce myself, I'm jarvis your virtual assistance. built with an inspiration of Tony Stark's Jarvis.")
                break
            else:
                speak("No face detected. Please align properly.")
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        handle_error("register_new_face", e)

def face_login():
    try:
        known_encodings, known_names = load_known_faces()
        cap = cv2.VideoCapture(0)
        speak("Starting facial recognition...")
        attempts = 0
        while attempts < 3:
            ret, frame = cap.read()
            if not ret:
                speak("Camera error.")
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_encodings(rgb)
            if faces:
                match = face_recognition.compare_faces(known_encodings, faces[0])
                if True in match:
                    speak(f"Access granted, Welcome back {known_names[match.index(True)]}.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    speak("Unauthorized face detected.")
                    attempts += 1
            else:
                speak("No face detected. Please align.")
            cv2.imshow("Login - Press Q to cancel", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                speak("Login cancelled.")
                break

        cap.release()
        cv2.destroyAllWindows()
        speak("Face authentication failed.")

        # 🔐 Ask for registration after 3 failed attempts
        speak("Would you like to register a new face? Say 'yes' or 'no'.")
        response = listen()
        if "yes" in response:
            register_new_face()
            return face_login()  # Retry login after registration
        else:
            speak("Access denied. Shutting down.")
            sys.exit()
    except Exception as e:
        handle_error("face_login", e)
        if 'cap' in locals():
            cap.release()
            cv2.destroyAllWindows()
        return False

def welcome_greeting():
    from datetime import datetime
    now = datetime.now().hour
    if now < 12:
        speak("Good morning, sir.")
    elif now < 18:
        speak("Good afternoon, sir.")
    else:
        speak("Good evening, sir.")
