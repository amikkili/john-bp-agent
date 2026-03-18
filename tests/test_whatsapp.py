from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing WhatsApp...")
print(f"Sending TO: {os.getenv('DOCTOR_WHATSAPP')}")

client = Client(
    os.getenv("TWILIO_SID"),
    os.getenv("TWILIO_TOKEN")
)

msg = client.messages.create(
    from_="whatsapp:+14155238886",
    to=os.getenv("DOCTOR_WHATSAPP"),
    body="TEST: John BP Agent alert — BP 155 CRITICAL!"
)

print(f"Status: {msg.status}")
print(f"SID: {msg.sid}")
print("Check your WhatsApp now!")