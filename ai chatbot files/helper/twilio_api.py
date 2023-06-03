import os
import random

from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_TOKEN')
client = Client(account_sid, auth_token)


def send_message(to: str, message: str) -> None:
    _ = client.messages.create(from_='whatsapp:+14155238886',
                               body=message,
                               to=to)
