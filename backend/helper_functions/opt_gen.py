import os
import asyncio
from dotenv import load_dotenv
import random
import smtplib
from email.message import EmailMessage

def generate_OTP():
    randNum=random.randint(0, 999999)
    paddedRandNum=f"{randNum:06d}"
    return paddedRandNum

