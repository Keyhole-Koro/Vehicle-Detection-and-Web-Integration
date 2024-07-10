import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def send_error_email(error_message):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT = os.getenv("EMAIL_SMTP_PORT")
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS").split(',')

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(EMAIL_RECIPIENTS)
    msg['Subject'] = "Error Notification: POST Request Failure"

    body = f"An error occurred during the POST request:\n\n{error_message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_RECIPIENTS, msg.as_string())
        print("Error email sent successfully.")
    except Exception as e:
        print(f"Failed to send error email: {e}")
