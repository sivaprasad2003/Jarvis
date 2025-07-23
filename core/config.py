# core/config.py

# === API Keys ===
import os
GEMINI_API_KEY = "AIzaSyDAJfovc7LPw8cr6bzaz7fxME3N5bINX70"  # Replace with your actual Gemini API key

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
