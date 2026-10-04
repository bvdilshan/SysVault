import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backup import load_config
from logger import logger
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(subject, body):
    config = load_config()
    email_cfg = config.get("email_notifications", {})

    if not email_cfg.get("enabled", False):
        return

    smtp_server = email_cfg.get("smtp_server")
    smtp_port = email_cfg.get("smtp_port", 587)
    sender_email = email_cfg.get("sender_email")
    sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
    receiver_email = email_cfg.get("receiver_email")

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email alert sent successfully to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")