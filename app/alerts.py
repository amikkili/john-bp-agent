from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp(message: str):
    client = Client(
        os.getenv("TWILIO_SID"),
        os.getenv("TWILIO_TOKEN")
    )
    client.messages.create(
        from_="whatsapp:+14155238886", # Twilio sandbox
        to=os.getenv("DOCTOR_WHATSAPP"),
        body=message
    )
    print(f"WhatsApp sent: {message[:60]}")