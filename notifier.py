"""
Notifier — sends the morning briefing via email (HTML) and prints to console.
"""
from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import config


def send_email(text_body: str, html_body: str) -> bool:
    if not config.NOTIFICATION_EMAIL or not config.SMTP_USER:
        print("[notifier] Email not configured — skipping send.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ Morning Briefing — {datetime.now().strftime('%a %b %d')}"
    msg["From"] = config.SMTP_USER
    msg["To"] = config.NOTIFICATION_EMAIL

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, config.NOTIFICATION_EMAIL, msg.as_string())
        print(f"[notifier] Briefing emailed to {config.NOTIFICATION_EMAIL}")
        return True
    except Exception as e:
        print(f"[notifier] Email failed: {e}")
        return False
