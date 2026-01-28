import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
WHISPER_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

def transcribe_audio(audio_file_path):
    """
    Transcribes audio file to text using Whisper API.
    """
    if not os.path.exists(audio_file_path):
        return "Error: Audio file not found."

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    with open(audio_file_path, "rb") as f:
        data = f.read()

    try:
        response = requests.post(WHISPER_URL, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")
    except Exception as e:
        print(f"Transcription Error: {e}")
        return "Error during transcription."
