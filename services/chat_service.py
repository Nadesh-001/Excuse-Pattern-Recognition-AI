import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Load keys from environment only
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_chat_response(user_message, conversation_history, user_context=""):
    """
    Chat response using:
    1. Groq (Primary)
    2. Gemini (Fallback)
    """

    system_prompt = f"""
You are a helpful AI assistant for a task management system.

Context about user:
{user_context}

Help users with:
- Task management
- Time management
- Delay analysis
- Work-related guidance

Be concise, helpful, and professional.
""".strip()

    # =========================
    # 1️⃣ GROQ (PRIMARY)
    # =========================
    try:
        if not GROQ_API_KEY:
            raise ValueError("Groq API key missing")

        client = Groq(api_key=GROQ_API_KEY)

        messages = (
            [{"role": "system", "content": system_prompt}]
            + conversation_history
            + [{"role": "user", "content": user_message}]
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"[Groq Error] {e}")

    # =========================
    # 2️⃣ GROQ SECONDARY (FALLBACK)
    # =========================
    # Model: openai/gpt-oss-safeguard-20b
    try:
        secondary_key = os.getenv("GROQ_API_KEY_SECONDARY")
        if not secondary_key:
            raise ValueError("Secondary Groq API key missing")

        client_secondary = Groq(api_key=secondary_key)

        history_text = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in conversation_history
        )

        prompt = f"""
{system_prompt}

Conversation History:
{history_text}

User: {user_message}
Assistant:
""".strip()

        # Check if history format needs adjustment for Groq, usually messages list is better
        # Re-using messages list but with secondary client
        messages = (
            [{"role": "system", "content": system_prompt}]
            + conversation_history
            + [{"role": "user", "content": user_message}]
        )

        completion = client_secondary.chat.completions.create(
            model="llama3-8b-8192", # Valid fallback model
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"[Groq Secondary Error] {e}")
        return "⚠️ AI service unavailable. Both primary and backup systems failed."
