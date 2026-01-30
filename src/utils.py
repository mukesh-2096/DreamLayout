import random
import string
import requests
from src.config import Config

def generate_verification_code(length=6):
    """Generate a random alphanumeric verification code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_verification_email(recipient, code, step=1):
    """
    Send verification email using Resend API
    step 1: Approval for old email
    step 2: Verification for new email
    """
    if step == 1:
        subject = "Approve Email Change - DreamLayout"
        message = f"You requested an email change. Please enter this code to approve the change: {code}"
    else:
        subject = "Verify Your New Email - DreamLayout"
        message = f"Please enter this code to verify your new email address: {code}"

    # Resend API call
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {Config.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": f"DreamLayout <{Config.MAIL_DEFAULT_SENDER}>",
        "to": [recipient],
        "subject": subject,
        "html": f"""
            <div style="font-family: sans-serif; padding: 40px; background-color: #f9fafb; border-radius: 24px;">
                <h1 style="color: #4f46e5; font-size: 24px; font-weight: 800; margin-bottom: 20px;">DreamLayout Security</h1>
                <p style="color: #4b5563; font-size: 16px; font-weight: 600;">{message}</p>
                <div style="margin-top: 30px; padding: 20px; background-color: #ffffff; border-radius: 16px; text-align: center; border: 1px solid #e5e7eb;">
                    <span style="font-size: 32px; font-weight: 900; letter-spacing: 5px; color: #111827;">{code}</span>
                </div>
                <p style="margin-top: 30px; color: #9ca3af; font-size: 12px;">If you did not request this change, please ignore this email.</p>
            </div>
        """
    }

    try:
        # If no API key is set, we skip the real call and log to console for development
        if not Config.RESEND_API_KEY or Config.RESEND_API_KEY == '':
            print(f"--- DEV MODE: EMAIL API KEY MISSING ---")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(f"Code: {code}")
            return True

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            print(f"Resend API Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error calling Email API: {e}")
        return False
