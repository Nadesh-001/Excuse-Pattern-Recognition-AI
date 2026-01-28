
import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def analyze_delay_reason(reason_text, user_history_summary="No prior history"):
    """
    Analyzes delay reason using Gemini (Primary) or Groq (Backup).
    Returns structured JSON: {authenticity: int, avoidance: int, risk_level: str, analysis: str}
    """
    
    prompt = f"""
    Analyze the following excuse for a task deadline delay.
    Excuse: "{reason_text}"
    User History: {user_history_summary}
    
    Evaluate:
    1. Authenticity Score (1-100%): How truthful/verifiable?
    2. Avoidance Score (1-100%): Is user shifting blame?
    3. Risk Level: Low, Medium, High
    4. Brief Analysis (1 sentence)
    
    Output strictly in JSON format:
    {{
        "authenticity": 85,
        "avoidance": 10,
        "risk_level": "Low",
        "analysis": "Reasonable and verifiable."
    }}
    """
    
    # 1. Try Groq (Primary - Verified)
    try:
        if not GROQ_API_KEY:
            raise ValueError("No Groq Key")
            
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON-only analyzer."},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Analysis Failed: {e}")

    # 2. Fallback to Gemini
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        text = response.text
        # Clean markdown
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        # Final Fallback
        return {
            "authenticity": 50,
            "avoidance": 50,
            "risk_level": "Medium",
            "analysis": "AI Analysis Unavailable. Manual review required."
        }
