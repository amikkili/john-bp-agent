from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Groq uses OpenAI SDK — just change base_url
groq = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ask_groq(prompt: str) -> str:
    """Send any question to Groq and get answer"""
    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical AI assistant. "
                           "Analyse patient vitals and medicines. "
                           "Be concise and precise."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
