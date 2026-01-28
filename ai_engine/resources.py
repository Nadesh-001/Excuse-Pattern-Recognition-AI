
import os
import json
import requests
import google.generativeai as genai
from groq import Groq
from bs4 import BeautifulSoup
# from PyPDF2 import PdfReader # Optional if we need deep PDF parsing

from .core import GEMINI_API_KEY, GROQ_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def parse_file(file_path):
    # Simple text extraction for now
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        # Add PDF logic here if needed
        return f"File content of {os.path.basename(file_path)}" 
    except:
        return ""

def parse_url(url):
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        return soup.get_text()[:5000] # Limit content
    except:
        return ""

def analyze_resource(content):
    """
    Summarizes content and extracts deadlines.
    """
    prompt = f"""
    Analyze this resource content:
    {content[:4000]}...
    
    1. Summarize in 2 sentences.
    2. Extract any extracted deadlines (dates).
    3. Rate completeness (1-100%).
    
    JSON Output:
    {{
        "summary": "...",
        "deadlines": ["YYYY-MM-DD"],
        "completeness": 80
    }}
    """
    
    # 1. Try Groq (Primary - Verified)
    try:
        if not GROQ_API_KEY: raise ValueError("No Groq Key")
        client = Groq(api_key=GROQ_API_KEY)
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"}
        )
        return json.loads(chat.choices[0].message.content)
    except Exception as e:
        print(f"Groq Resource Analysis Failed: {e}")

    # 2. Fallback to Gemini
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"summary": "Analysis Unavailable", "deadlines": [], "completeness": 0}
