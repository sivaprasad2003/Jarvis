# JARVIS AI Assistant 💻🎙️🤖

JARVIS is your personal AI assistant that understands voice commands, recognizes faces, detects objects, manages system functions, and even chats with you using Google Gemini AI.

---

## 🚀 Features

- 🔐 **Face Authentication** (Login using your face)
- 🎧 **Voice Recognition** using SpeechRecognition
- 🧠 **Chat with Gemini AI** (via Google Generative AI API)
- 🧏‍♂️ **Speech Output** using pyttsx3
- 🎥 **Real-time Object Detection** (with OpenCV + cvlib)
- 🎼 **Media Control** (play/pause, YouTube, Spotify)
- 🎛️ **System Controls** (shutdown, restart, hibernate, volume, mute)
- 🔋 **System Info** (battery, CPU, RAM, Disk)
- 🧠 **Memory System** (remember things you say)
- 📸 **Screenshots via voice**
- 🎨 Optional GUI via CustomTkinter

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Jarvis.git
cd Jarvis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> 💡 If installing `dlib` fails, Use Precompiled dlib.whl in Packages older according python version 3.x or download the `.whl` for your system from: https://github.com/z-mahmud22/Dlib_Windows_Python3.x

### 4. Configure Gemini AI

Go To https://aistudio.google.com/apikey sign in with your google account

Create API key and Copy that API key 

Open `core/config.py` and Paste the API over Placeholder:

```python
GEMINI_API_KEY = "your_actual_google_gemini_api_key"
```

---

## ▶️ How to Run

```bash
python main.py
```

---

## 📂 Project Structure

```
Jarvis/
│
├── core/
│   ├── face_auth.py         # Face recognition login
│   ├── speech.py            # TTS and voice input
│   ├── gemini_ai.py         # Gemini AI integration
│   ├── object_detection.py  # Real-time camera object detection
│   ├── media_control.py     # YouTube/Spotify controls
│   ├── memory.py            # Memory storage
│   ├── gui.py               # Optional GUI (CustomTkinter)
│   ├── utils.py             # Error handling & helpers
│   ├── config.py            # API keys and constants
│   └── command_center.py    # Voice command center
│
├── authorized_faces/        # Stores registered face images
├── requirements.txt
└── main.py                  # Entry point
```

---

## 📸 Face Authentication

Place `.jpg` or `.png` images in `authorized_faces/` or enroll new face via the assistant.

---

## 💡 Example Commands

- `"what time is it"`  
- `"increase volume"`  
- `"shutdown system"`  
- `"object detection"`  
- `"activate ai"` → `"What's the capital of Japan?"`  
- `"remember this is my password"` → `"what did I tell you?"`  

---

## 🧠 To-Do / Ideas

- [ ] Add real reminders & alarm system  
- [ ] Integrate YouTube Music/Spotify API  
- [ ] Add emotion detection and sentiment response  
- [ ] Add voice training & wake-word customization  

---

## 👨‍💻 Author

Made with ❤️ by Tony Stark (Sivaprasad)  
📧 Contact: sivaprasad10072003@gmail.com.com

---

## 📄 License

This project is for educational use. Commercial usage must comply with the terms of the APIs used (e.g. Google Gemini).
