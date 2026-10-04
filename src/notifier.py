import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backup import load_config
from logger import logger
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

def send_email_alert(subject, body):
    config = load_config()
    email_cfg = config.get("email_notifications", {})

    if not email_cfg.get("enabled", False):
        return

    smtp_server = email_cfg.get("smtp_server", "smtp.gmail.com")
    smtp_port = email_cfg.get("smtp_port", 465)
    sender_email = email_cfg.get("sender_email")
    sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
    receiver_email = email_cfg.get("receiver_email")

    if not sender_password:
        logger.error(f"Email sender password not set in environment variables (Checkedf path: {ENV_PATH})")
        return  

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=20) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)  
                server.ehlo()
                server.login(sender_email, sender_password)
                server.send_message(msg)

        logger.info(f"Email alert sent successfully to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}", exc_info=True)