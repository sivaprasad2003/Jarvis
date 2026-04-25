import sqlite3
import datetime
import json
from core.speech import speak
from core.utils import handle_error

MEMORY_DB = "memory.db"

def _init_db():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organized_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            category TEXT,
            subject TEXT,
            details TEXT,
            raw_fact TEXT
        )
    ''')
    conn.commit()
    conn.close()

_init_db()

def _extract_memory_structure(fact):
    prompt = f"""
    Analyze the following memory fact and extract its core components into a JSON object.
    Do not return any other text, just the raw JSON object.
    Keys required:
    - "category": Broad category (e.g., 'Personal', 'Work', 'Preferences', 'Event', 'General')
    - "subject": The main entity or subject (e.g., 'Tony', 'Project X', 'Dinner', 'Car')
    - "details": The specific information to remember.
    
    Fact to analyze: "{fact}"
    """
    try:
        response = ask_gemini_fallback(prompt)
        
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
            
        return json.loads(response.strip())
    except Exception as e:
        print(f"[Memory Extraction Error] {e}")
        return {"category": "General", "subject": "Unknown", "details": fact}

def remember_this(fact):
    try:
        speak("Organizing memory...")
        structured_data = _extract_memory_structure(fact)
        category = structured_data.get("category", "General")
        subject = structured_data.get("subject", "Unknown")
        details = structured_data.get("details", fact)
        
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO organized_memory (timestamp, category, subject, details, raw_fact) 
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, category, subject, details, fact))
        conn.commit()
        conn.close()
        speak(f"Got it. I filed that under {category}, concerning {subject}.")
    except Exception as e:
        handle_error("remember_this", e)
        speak("I encountered an issue saving to my organized memory database.")

def recall_memory():
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT category, subject, details FROM organized_memory ORDER BY category, subject ASC")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            speak("Let me consult my archives, sir...")
            
            memory_list = ""
            for row in rows:
                category, subject, details = row
                memory_list += f"- Category: {category}, Subject: {subject}, Details: {details}\n"
                
            prompt = f"""
            You are J.A.R.V.I.S., Tony Stark's highly advanced AI assistant. 
            The user has asked you to recall their memories. Here are the facts stored in your database:
            
            {memory_list}
            
            Please provide a conversational, sophisticated, and concise summary of these memories.
            Address the user as 'Sir' or 'Boss'. Group related things together intelligently. 
            Do not list them mechanically. Speak naturally and elegantly as Jarvis would.
            """
            
            response = ask_gemini_fallback(prompt)
            
            # Clean up response if needed
            if response.startswith("```"):
                response = response.split("\n", 1)[-1]
            if response.endswith("```"):
                response = response[:-3]
                
            speak(response.strip())
        else:
            speak("I don't have anything stored in my memory banks at the moment, sir.")
    except Exception as e:
        handle_error("recall_memory", e)
        speak("I'm sorry, sir. My memory database appears to be corrupted or inaccessible.")
