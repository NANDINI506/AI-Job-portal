import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, body, from_email=None, app_password=None):
    """
    Send an email using Gmail SMTP.
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body (plain text or HTML)
        from_email (str): Sender's Gmail address (if None, use EMAIL_SENDER env var)
        app_password (str): Gmail app password (if None, use GMAIL_APP_PASSWORD env var)
    """
    from_email = from_email or os.environ.get('EMAIL_SENDER')
    app_password = app_password or os.environ.get('GMAIL_APP_PASSWORD')
    if not from_email or not app_password:
        raise ValueError("Missing sender email or app password.")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        raise 