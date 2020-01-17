import email
import os
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def main():

    email_body = os.getenv('BODY')
    email_recepient = os.getenv('TO')
    email_sender = os.getenv('FROM')
    email_subject = os.getenv('SUBJECT')
    mime_type = os.getenv('MIME_TYPE', 'plain')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_port = os.getenv('SMTP_PORT', 25)
    smtp_server = os.getenv('SMTP_SERVER')

    message = MIMEMultipart()
    message["Subject"] = email_subject
    message["From"] = email_sender
    message["To"] = email_recepient

    message_body = MIMEText(email_body, mime_type)

    message.attach(message_body)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_username, smtp_password)
    server.sendmail(
        email_sender, email_recepient, message.as_string()
    )
    server.quit()

if __name__ == "__main__":
    main()