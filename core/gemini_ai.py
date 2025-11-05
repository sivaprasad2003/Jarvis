# core/gemini_ai.py
import google.generativeai as genai
from core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt, model_name="gemini-2.5-flash", retries=2):
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if attempt == retries - 1:
                return f"[Gemini Error]: {e}"
    return "I'm sorry, I couldn't process that request."

def ask_gemini_fallback(prompt):
    response = ask_gemini(prompt, "gemini-2.5-flash")
    if "[Gemini Error]" in response:
        response = ask_gemini(prompt, "gemini-2.5-pro")
    return response
