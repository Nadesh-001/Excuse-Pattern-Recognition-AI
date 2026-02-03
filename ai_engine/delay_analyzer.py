import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# --- Configuration ---
# Look in secrets first (for Cloud), then env (for local)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def validate_analysis_result(result):
    """Validate that AI analysis has all required fields."""
    required_fields = ['authenticity_score', 'category', 'risk_level', 'avoidance_score', 'recommendations']
    
    if not isinstance(result, dict):
        return False
    
    for field in required_fields:
        if field not in result:
            print(f"⚠️ Missing field in AI result: {field}")
            return False
    
    # Validate score ranges
    if not (0 <= result.get('authenticity_score', -1) <= 100):
        print(f"⚠️ Invalid authenticity_score: {result.get('authenticity_score')}")
        return False
    if not (0 <= result.get('avoidance_score', -1) <= 100):
        print(f"⚠️ Invalid avoidance_score: {result.get('avoidance_score')}")
        return False
    
    # Validate risk level
    if result.get('risk_level') not in ['Low', 'Medium', 'High']:
        print(f"⚠️ Invalid risk_level: {result.get('risk_level')}")
        return False
    
    return True

def analyze_delay(reason_text, user_history_summary="No prior history"):
    """
    Analyzes delay reason using specific prompt structure.
    Returns structured JSON with authenticity, category, risk, avoidance, recommendations.
    """
    
    prompt = f"""
    Analyze the following excuse for a task deadline delay in a professional setting.
    Excuse: "{reason_text}"
    User History context: {user_history_summary}
    
    Evaluate and provide analysis in Strict JSON format:
    1. authenticity_score (0-100): How truthful/verifiable?
    2. category: "Health | Personal | Technical | External | Workload | Communication | Other"
    3. risk_level: "Low | Medium | High"
    4. avoidance_score (0-100): Measure of blame shifting or avoiding responsibility.
    5. recommendations: Specific text advice for the manager or employee.
    
    JSON Output Example:
    {{
        "authenticity_score": 82,
        "category": "Technical",
        "risk_level": "Low",
        "avoidance_score": 20,
        "recommendations": "Verify server logs."
    }}
    """
    
    # 1. Try Groq (Primary)
    try:
        if not GROQ_API_KEY:
            print("⚠️ No Groq API key found")
            raise ValueError("No Groq Key")
        
        print("🔄 Attempting analysis with Groq (mixtral-8x7b-32768)...")
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON-only analyzer for workforce patterns."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            response_format={"type": "json_object"},
            timeout=30
        )
        result = json.loads(chat_completion.choices[0].message.content)
        
        if validate_analysis_result(result):
            print("✅ Groq analysis successful")
            return result
        else:
            print("⚠️ Groq returned invalid result format")
            raise ValueError("Invalid result format")
            
    except Exception as e:
        print(f"❌ Groq (mixtral) failed: {e}")
        # Fallback to gpt-oss-20b
        try:
            print("🔄 Attempting fallback to Groq (gpt-oss-20b)...")
            client = Groq(api_key=GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                response_format={"type": "json_object"},
                timeout=30
            )
            result = json.loads(chat_completion.choices[0].message.content)
            
            if validate_analysis_result(result):
                print("✅ Groq fallback successful")
                return result
        except Exception as e2:
            print(f"❌ Groq fallback also failed: {e2}")

    # 2. Fallback to Gemini
    try:
        if not GEMINI_API_KEY:
            print("⚠️ No Gemini API key found")
            raise ValueError("No Gemini Key")
        
        print("🔄 Attempting analysis with Gemini...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        if validate_analysis_result(result):
            print("✅ Gemini analysis successful")
            return result
        else:
            print("⚠️ Gemini returned invalid result format")
            
    except Exception as e:
        print(f"❌ Gemini Analysis Failed: {e}")
    
    # Final Fallback
    print("⚠️ All AI providers failed, using fallback values")
    return {
        "authenticity_score": 50,
        "category": "Other",
        "risk_level": "Medium",
        "avoidance_score": 50,
        "recommendations": "AI Analysis Unavailable. Manual review required."
    }
