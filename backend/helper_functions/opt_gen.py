import os
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

async def email_OTP(otp,email):
    msg = EmailMessage()
    msg["Subject"] = "OTP Email"
    msg["From"] = EMAIL
    msg["To"] = email
    msg.set_content(f"OTP for Password Reset {otp}")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
