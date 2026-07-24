import os
import asyncio
from dotenv import load_dotenv
from .opt_gen import generate_OTP
import smtplib
from email.message import EmailMessage
load_dotenv()
EMAIL=os.getenv("EMAIL")
APP_PASSWORD=os.getenv("APP_PASSWORD")


def _send_email_sync(otp, email,action_type):
    content=f"Your code for {action_type} is {otp}."
    """Synchronous SMTP sender — runs in a thread via asyncio.to_thread."""
    msg = EmailMessage()
    msg["Subject"] = "OTP Email"
    msg["From"] = EMAIL
    msg["To"] = email
    msg.set_content(f"{content}\n"
                    f"This code will expire in 10 minutes.\n"
                    f"If you did not request this code, please ignore this message.\n")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print(f"[OTP] Email sent to {email}")
    except Exception as e:
        print(f"[OTP Notice] SMTP failed: {e}. OTP for {email} is: {otp}")

async def email_OTP(otp, email,action_type):
    """Non-blocking OTP email dispatch."""
    await asyncio.to_thread(_send_email_sync, otp, email,action_type)

def _send_collaborator_email_sync(email, name, temp_password, project_name):
    msg = EmailMessage()
    msg["Subject"] = f"Welcome to Project Workspace: {project_name}"
    msg["From"] = EMAIL
    msg["To"] = email
    msg.set_content(
        f"Hello {name},\n\n"
        f"You have been added as an External Collaborator to the project '{project_name}'.\n\n"
        f"Here are your login credentials:\n"
        f"Email: {email}\n"
        f"Temporary Password: {temp_password}\n\n"
        f"Please log in to access your project workspace and team chat."
    )
    try:
        if EMAIL and APP_PASSWORD:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as smtp:
                smtp.starttls()
                smtp.login(EMAIL, APP_PASSWORD)
                smtp.send_message(msg)
            print(f"[Email] Welcome email sent to {email}")
        else:
            print(f"[Email Notice] SMTP credentials not in .env. Password for {email} is: {temp_password}")
    except Exception as e:
        print(f"[Email Notice] SMTP failed: {e}. Password for {email} is: {temp_password}")

async def email_collaborator_welcome(email, name, temp_password, project_name):
    await asyncio.to_thread(_send_collaborator_email_sync, email, name, temp_password, project_name)


def _send_due_reminder_email_sync(email, task_name, due_date_str, project_name=""):
    msg = EmailMessage()
    msg["Subject"] = f"⏰ Task Reminder: '{task_name}' is due soon!"
    msg["From"] = EMAIL
    msg["To"] = email
    msg.set_content(
        f"Hello,\n\n"
        f"This is an automated reminder that your assigned task '{task_name}' in project '{project_name}' has less than 1 day remaining before its due date.\n\n"
        f"Due Date: {due_date_str}\n"
        f"Kindly complete it as soon as possible"
    )
    try:
        if EMAIL and APP_PASSWORD:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as smtp:
                smtp.starttls()
                smtp.login(EMAIL, APP_PASSWORD)
                smtp.send_message(msg)
            print(f"[Email] Task due reminder email sent to {email}")
        else:
            print(f"[Email Notice] SMTP credentials not set in .env. Task reminder for '{task_name}' due: {due_date_str} to {email}")
    except Exception as e:
        print(f"[Email Notice] SMTP failed: {e}. Task reminder for '{task_name}' due: {due_date_str} to {email}")


async def send_task_due_reminder_email(email: str, task_name: str, due_date_str: str, project_name: str = ""):
    """Dispatch due date reminder email asynchronously."""
    await asyncio.to_thread(_send_due_reminder_email_sync, email, task_name, due_date_str, project_name)
