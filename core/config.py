# core/config.py

# === API Keys ===
import os
GEMINI_API_KEY = "AIzaSyDAJfovc7LPw8cr6bzaz7fxME3N5bINX70"  # Replace with your actual Gemini API key
OPENWEATHERMAP_API_KEY = "b6907d289e10d714a6e88b30761fae22"  # OpenWeatherMap demo key
NEWSAPI_KEY = "17e5fc4b600b42828b1ba1faf08d17ef"

# === Assistant Settings ===
WAKE_WORD = "jarvis"
STANDBY_MODE = False
AI_MODE = False
# === Memory Placeholder ===
# MEMORY_STORE is used to temporarily store assistant memory; expected format is a string (can be replaced with a more complex structure as needed).
MEMORY_STORE = ""

import os
# Disable oneDNN optimizations to avoid potential TensorFlow errors on some CPUs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
