# JARVIS AI Assistant 💻🎙️🤖

JARVIS is your personal AI assistant that understands voice commands, recognizes faces, seamlessly launches Windows applications, detects objects using AI vision, manages system functions, and even chats with you dynamically using Google Gemini AI or offline local LLM via Ollama.

---

## 🚀 Key Features

*   🔐 **Face Authentication Login**: Securely authenticate using your face. Drop images of known users into `known_faces/` or seamlessly enroll new users via voice.
*   🎧 **True Background Voice Recognition**: Uses `SpeechRecognition` to run silently in the background, gracefully ignoring ambient chatter and TV noise until the wake word is spoken.
*   🧠 **Conversational Gemini AI**: Fully integrated with Google Generative AI (`gemini-2.5-flash`). Say "activate AI mode" to drop the wake word requirement and chat naturally.
*   🤖 **Offline AI with Ollama**: Local LLM support using TinyLlama for instant responses, code generation, and intent classification without internet dependency.
*   🧏‍♂️ **Native SAPI5 TTS Engine**: Custom-integrated native Windows TTS (`SAPI.SpVoice`) running on its own dedicated Thread Queue. JARVIS never hangs, never skips lines, and delivers flawless, synchronous vocal responses.
*   🚀 **Ghost-Protocol App Launcher**: Take native OS control. Say `open [app name]` and JARVIS instantly executes a macro to press your Windows key, securely type the application name, and launch it (just like a human would).
*   🎥 **Real-time Object Detection**: Uses OpenCV to analyze your camera feed and vocally describe what he sees when asked.
*   🎼 **Comprehensive Media Control**: Play/pause, next/previous tracks, mute, change volume, and search+play any song directly on YouTube.
*   🎛️ **Advanced System Controls**: Shutdown, restart, hibernate, lock your workstation, run speed tests, check CPU temperatures, fan speeds, and exact battery health.
*   🧠 **Contextual Memory**: Ask JARVIS to remember facts, passwords, or data, which he saves persistently across reboots to a discrete JSON file.
*   📸 **Screenshot Capabilities**: Capture, view, and organize screenshots entirely by voice command.
*   🪟 **Window Management**: Switch windows, close apps, minimize all, and control desktop.
*   📋 **Clipboard & System Utilities**: Read clipboard, empty recycle bin, clear temp files, and optimize system.
*   ⏰ **Reminders & Alarms**: Set timed reminders and get current time/date information.
*   😂 **Entertainment**: Tell jokes, fetch news headlines, and check weather forecasts.
*   🌐 **Connectivity Controls**: Toggle WiFi and Bluetooth.
*   🎨 **Theme Switching**: Switch between dark and light modes.

---

## 🛠️ Complete Setup Instructions

Follow these instructions perfectly to ensure all native Windows COM APIs and AI modules align safely.

### 1. Clone the Repository

```bash
git clone https://github.com/sivaprasad2003/Jarvis.git
cd Jarvis
```

### 2. Prepare the Python Environment (Crucial Step)

Due to a strict C++ ABI memory alignment requirement for Dlib and OpenCV face recognition, **you must use Python 3.11** or **Python 3.12**.
We highly recommend creating an isolated Virtual Environment named `venv_jarvis`.

```powershell
python -m venv venv_jarvis
.\venv_jarvis\Scripts\Activate.ps1
```

### 3. Install Pre-Compiled C++ Core Dependencies

To bypass hours of compiling Dlib locally via Microsoft Visual Studio tools, pre-compiled wheels are provided in the `Packages/` directory for Python 3.11/3.12.

**For Python 3.11:**
```powershell
pip install Packages/dlib-19.24.1-cp311-cp311-win_amd64.whl
```
**For Python 3.12:**
```powershell
pip install Packages/dlib-19.24.99-cp312-cp312-win_amd64.whl
```

### 4. Install Remaining Packages & Restrict Numpy

Next, install all other universal dependencies safely:
```powershell
pip install -r requirements.txt
```
> ⚠️ **Note on NumPy**: The `requirements.txt` specifically locks `numpy < 2.0.0`. Do not upgrade NumPy into the `2.x` branches. The pre-compiled Dlib native wheels will throw a total `Unsupported Image Type` C-Contiguous RuntimeError if NumPy 2.x is used!

### 5. Install Ollama for Offline AI (Optional but Recommended)

For offline AI capabilities, install Ollama and pull the TinyLlama model:
1. Download and install Ollama from [ollama.ai](https://ollama.ai/).
2. Open a terminal and run:
```powershell
ollama pull tinyllama
```
This enables local LLM queries, code generation, and intent classification without requiring an internet connection.



## 📸 Adding Faces for Authentication

To allow JARVIS to recognize you instantly on boot:
1. Create a folder locally named `known_faces/` in your root directory.
2. Drop pictures of yourself (`.jpg`, `.png`, `.jpeg`). You can name the file your name (e.g. `Tony_Stark.jpg`).
3. Next time you boot, JARVIS will automatically process the memory array safely matching the precise RGB formats needed and authorize you.

Alternatively, JARVIS will vocally ask to scan your face via the webcam on boot if he does not recognize you after 3 attempts. 

---

## ▶️ How to Run

Ensure your virtual environment is activated, then simply run the main loop:

```powershell
python main.py
```

---

## 💡 Top Example Commands

Once the system boots and you pass Facial Recognition, say "**Jarvis**" followed by an action:

*   **App Launching**: `"Jarvis, open google chrome"` | `"Jarvis, open calculator"` | `"Jarvis, open discord"`
*   **System Controls**: `"Jarvis, shutdown system"` | `"Jarvis, lock system"` | `"Jarvis, hibernate system"`
*   **Media Control**: `"Jarvis, play media"` | `"Jarvis, volume up"` | `"Jarvis, mute"` | `"Jarvis, play Bohemian Rhapsody on youtube"`
*   **Object Detection**: `"Jarvis, start object detection"` | `"Jarvis, what do you see"`
*   **Screenshots**: `"Jarvis, take screenshot"` | `"Jarvis, show last screenshot"`
*   **Memory**: `"Jarvis, remember my password is 1234"` | `"Jarvis, what do you remember"`
*   **Window Management**: `"Jarvis, switch window"` | `"Jarvis, close this window"` | `"Jarvis, minimize all"`
*   **Utilities**: `"Jarvis, read clipboard"` | `"Jarvis, empty recycle bin"` | `"Jarvis, clear temp files"`
*   **Information**: `"Jarvis, what time is it"` | `"Jarvis, weather"` | `"Jarvis, speed test"` | `"Jarvis, system status"`
*   **Reminders**: `"Jarvis, set reminder for 5 minutes"`
*   **Entertainment**: `"Jarvis, tell me a joke"` | `"Jarvis, tell me the news"`
*   **AI Queries**: `"Jarvis, what is the capital of France"` | `"Jarvis, write code for a hello world program"`
*   **Themes**: `"Jarvis, enable dark mode"` | `"Jarvis, enable light mode"`
*   **Connectivity**: `"Jarvis, enable wifi"` | `"Jarvis, disable bluetooth"`

---
*   **Media**: `"Jarvis, play Interstellar Theme on youtube"` | `"Jarvis, pause media"` | `"Jarvis, set volume 40%"`
*   **AI Mode**: `"Jarvis, activate AI mode."` *(He will stop needing the wake-word -> have a normal fluid conversation using Gemini)* -> `"Deactivate AI mode."`
*   **System/Hardware**: `"Jarvis, system status"` | `"Jarvis, check CPU temperature"` | `"Jarvis, speed test"` 
*   **Memory**: `"Jarvis, remember my locker code is 8409"` -> Later: `"Jarvis, what do you remember?"`
*   **Vision**: `"Jarvis, start object detection"` -> `"Jarvis, what do you see?"`
*   **Utility**: `"Jarvis, show last screenshot"` | `"Jarvis, tell me the news"` | `"Jarvis, what's my IP address"`

*If you need JARVIS to abort all threads (like object detection or long background tasks), physically scream or urgently say:* **"Jarvis, emergency stop"**.

---

## 📂 Architecture Structure

```
Jarvis/
├── core/
│   ├── app_launcher.py      # WinKey automation + PyAutoGUI Macros
│   ├── battery_health.py    # Dedicated hardware parsing logic
│   ├── config.py            # API keys and constants
│   ├── face_auth.py         # Advanced array contiguous Dlib recognition
│   ├── gemini_ai.py         # Google Generative AI bindings
│   ├── media_control.py     # COM endpoint Pycaw handlers + keyboard injections
│   ├── memory.py            # Persistent JSON Fact Logging
│   ├── object_detection.py  # YOLO tracking and computer vision 
│   ├── shared_utils.py      # Core brain/switchboard indexing all commands
│   ├── speech.py            # Async Thread-Safe SAPI5 TTS Queue engine 
│   └── system_status.py     # CPU Thermals / WMI parsing
├── main.py                  # Entry Point execution
└── requirements.txt         # Package lock bindings
```

---

## 👨‍💻 Author
**Made with ❤️ by Tony Stark (Sivaprasad)**  
📧 Contact: sivaprasad10072003@gmail.com
