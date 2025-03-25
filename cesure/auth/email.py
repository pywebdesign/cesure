import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@cesure.com")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def send_email(to_email, subject, html_content):
    """
    Send an email using SMTP
    """
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        # For development, just print the email to console
        print(f"=== Email to: {to_email} ===")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        print("=== End of email ===")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_verification_email(user_id, email, verification_token):
    """
    Send an email verification link to a user
    """
    verification_url = f"{BASE_URL}/auth/verify-email?token={verification_token}"
    
    subject = "Verify your Cesure account"
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Cesure!</h2>
        <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>Or copy and paste this URL into your browser:</p>
        <p>{verification_url}</p>
        <p>If you didn't sign up for a Cesure account, you can safely ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)