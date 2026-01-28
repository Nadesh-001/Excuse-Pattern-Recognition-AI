
import streamlit as st
import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# --- AI Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(prompt, context=""):
    """
    Fetches response from Gemini (Primary).
    Falls back to Groq (Secondary) if Gemini fails.
    """
    full_prompt = f"{context}\n\nUser: {prompt}\nAI:"
    
    # 1. Try Groq (Primary - Verified)
    try:
        if not GROQ_API_KEY:
            raise ValueError("No Groq Key")
            
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an Excuse Pattern Recognition app."},
                {"role": "user", "content": full_prompt}
            ],
            # Verified working model (Groq V2 key)
            model="openai/gpt-oss-20b", 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        
    # 2. Fallback to Gemini
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: All AI services failed. \nGroq: Check logs. \nGemini: {str(e)}"

# --- Page Logic ---
st.title("🤖 AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask me anything about your tasks, delays, or patterns..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Context builder
            user_context = f"User: {st.session_state.user_name} ({st.session_state.user_role})"
            response = get_ai_response(prompt, context=user_context)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
