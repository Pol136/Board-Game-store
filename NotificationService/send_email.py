import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))
from_email = os.getenv("EMAIL_SENDER")
mail_password = os.getenv("MAIL_PASSWORD")


def send_email(subject, body, to_email: list):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ','.join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, mail_password)
        server.send_message(msg)
        print("Email sent successfully!", ','.join(to_email))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if server:
            server.quit()
