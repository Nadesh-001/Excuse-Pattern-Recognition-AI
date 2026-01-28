
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing Gemini Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Reply with 'Gemini Online'")
    print(f"✅ SUCCESS! Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
