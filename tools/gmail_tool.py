import smtplib
from email.mime.text import MIMEText
from config import DEFAULT_FROM_EMAIL, ADMIN_EMAIL
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = DEFAULT_FROM_EMAIL
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # <-- Put in .env

class GmailTool:
    async def send(self, to, subject, body):
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = DEFAULT_FROM_EMAIL
        msg["To"] = to

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(DEFAULT_FROM_EMAIL, [to], msg.as_string())

            return {"ok": True, "message": "Email sent successfully"}

        except Exception as e:
            return {"ok": False, "error": str(e)}
