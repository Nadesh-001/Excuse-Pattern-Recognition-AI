import google.generativeai as genai
from groq import Groq
import streamlit as st
import os

# Env loaded in app.py or delay_analyzer
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_chat_response(user_message, conversation_history, user_context=""):
    """
    Get chatbot response using Groq (Primary) or Gemini (Fallback).
    """
    
    system_prompt = f"""You are a helpful AI assistant for a task management system. 
    Context about user: {user_context}
    
    Help users with:
    - Task management and organization
    - Time management tips
    - Understanding delay patterns
    - General work-related questions
    
    Be concise, helpful, and professional."""
    
    # 1. Try Groq
    try:
        if not GROQ_API_KEY: raise ValueError("No Groq Key")
        
        client = Groq(api_key=GROQ_API_KEY)
        messages = [{"role": "system", "content": system_prompt}] + conversation_history + [{"role": "user", "content": user_message}]
        
        completion = client.chat.completions.create(
            # Using compliant model from master prompt request if possible, or fallback
            model="llama-3.3-70b-versatile", 
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Chat Failed: {e}")

    # 2. Gemini Fallback
    try:
        if not GEMINI_API_KEY: raise ValueError("No Gemini Key")
        model = genai.GenerativeModel('gemini-pro')
        
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        full_prompt = f"{system_prompt}\n\nHistory:\n{history_str}\n\nUser: {user_message}\nAssistant:"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Chat Failed: {e}")
        return "I apologize, check your API connections."
