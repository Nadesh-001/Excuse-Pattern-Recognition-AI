
import os
import sys
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Mock Streamlit for DB connection to fall back to os.getenv
import streamlit as st
if not hasattr(st, "secrets"):
    st.secrets = {}

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_connection

load_dotenv()

print("🚀 STARTING COMPLETENESS VERIFICATION 🚀\n")

# 1. Verify Database
print("--- 1. Testing Database Connection ---")
try:
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("✅ TiDB Database Connected Successfully!")
        conn.close()
    else:
        print("❌ Database Connection Failed (Check .env DB_HOST/USER/etc).")
except Exception as e:
    print(f"❌ Database Error: {e}")
print("\n")

# 2. Verify Gemini (Primary AI)
print("--- 2. Testing Gemini (Primary AI) ---")
try:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY missing in .env")
    else:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Gemini OK'")
        print(f"✅ Gemini Response: {response.text}")
except Exception as e:
    print(f"❌ Gemini Failed: {e}")
print("\n")

# 3. Verify Groq (Backup AI)
print("--- 3. Testing Groq (Backup AI) ---")
try:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("❌ GROQ_API_KEY missing in .env")
    else:
        client = Groq(api_key=key)
        # Using the verified working model
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'Groq OK'"}],
            model="openai/gpt-oss-20b" 
        )
        print(f"✅ Groq Response: {chat.choices[0].message.content}")
except Exception as e:
    print(f"❌ Groq Failed: {e}")
print("\n")

# 4. Verify Gmail API
print("--- 4. Testing Gmail API Configuration ---")
if os.path.exists("credentials.json"):
    print("✅ credentials.json found.")
else:
    print("❌ credentials.json MISSING.")

if os.path.exists("token.json"):
    print("✅ token.json found (Authenticated).")
else:
    print("⚠️ token.json not found. Run utils/gmail_setup.py to authenticate.")
print("\n")

print("🔍 VERIFICATION COMPLETE")
