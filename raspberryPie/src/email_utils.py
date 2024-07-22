import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def send_email(subject, body):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT = os.getenv("EMAIL_SMTP_PORT")
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS").split(',')

    # File to store the subjects of sent emails and their timestamps
    subject_file = 'sent_email_subjects.txt'
    cooldown_period = 300  # Cooldown period in seconds (5 minutes)

    def can_send_email(subject):
        if not os.path.exists(subject_file):
            return True
        with open(subject_file, 'r') as f:
            lines = f.readlines()
        current_timestamp = time.time()
        for line in lines:
            saved_subject, timestamp = line.strip().split('|')
            if saved_subject == subject and (current_timestamp - float(timestamp)) <= cooldown_period:
                return False
        return True

    def update_subject_list(subject):
        with open(subject_file, 'a') as f:
            f.write(f"{subject}|{time.time()}\n")

    if not can_send_email(subject):
        print(f"Cooldown period has not passed for subject '{subject}'. Email not sent.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(EMAIL_RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_RECIPIENTS, msg.as_string())
        print(f"Email '{subject}' sent successfully.")
        update_subject_list(subject)  # Update the list after sending the email
    except Exception as e:
        print(f"Failed to send email '{subject}': {e}")

def send_post_error_email(error_message):
    send_email("Error Notification: POST Request Failure", error_message)
