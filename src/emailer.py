import smtplib
from email.mime.text import MIMEText
from typing import List
from .config import SETTINGS

def send_summary(subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SETTINGS.smtp_sender
    msg["To"] = SETTINGS.smtp_to

    recipients = [x.strip() for x in SETTINGS.smtp_to.split(",") if x.strip()]
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SETTINGS.smtp_sender, SETTINGS.smtp_app_password)
        server.sendmail(SETTINGS.smtp_sender, recipients, msg.as_string())
