import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# --- AI Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(prompt, context=""):
    """
    Fetches response from Groq (Primary) or Gemini (Fallback).
    """
    full_prompt = f"{context}\n\nUser: {prompt}\nAI:"
    
    # 1. Try Groq (Primary)
    try:
        if not GROQ_API_KEY:
            raise ValueError("No Groq Key")
            
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an Excuse Pattern Recognition app."},
                {"role": "user", "content": full_prompt}
            ],
            model="openai/gpt-oss-20b", # Or llama3-70b-8192 if preferred
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        
    # 2. Fallback to Gemini
    try:
        if not GEMINI_API_KEY:
             return "Error: No AI API keys configured."
             
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: All AI services failed. \nGroq: Check logs. \nGemini: {str(e)}"
