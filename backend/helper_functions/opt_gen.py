import os
import asyncio
from dotenv import load_dotenv
import random
import smtplib
from email.message import EmailMessage
load_dotenv()
EMAIL=os.getenv("EMAIL")
APP_PASSWORD=os.getenv("APP_PASSWORD")

def generate_OTP():
    randNum=random.randint(0, 999999)
    paddedRandNum=f"{randNum:06d}"
    return paddedRandNum

#Simple Mail Transfer Protocol

def _send_email_sync(otp, email):
    """Synchronous SMTP sender — runs in a thread via asyncio.to_thread."""
    msg = EmailMessage()
    msg["Subject"] = "OTP Email"
    msg["From"] = EMAIL
    msg["To"] = email
    msg.set_content(f"OTP Number = {otp}")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print(f"[OTP] Email sent to {email}")
    except Exception as e:
        print(f"[OTP Notice] SMTP failed: {e}. OTP for {email} is: {otp}")

async def email_OTP(otp, email):
    """Non-blocking OTP email dispatch."""
    await asyncio.to_thread(_send_email_sync, otp, email)
