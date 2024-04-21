from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import mimetypes

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email(service, to_address, subject, body, attachment_path):
    # Création du message
    message = MIMEMultipart()
    message['to'] = to_address
    message['subject'] = subject

    # Corps du message
    text = MIMEText(body)
    message.attach(text)

    if attachment_path != '':
        # Pièce jointe
        with open(attachment_path, 'rb') as attachment:
            content_type, encoding = mimetypes.guess_type(attachment_path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            attachment = MIMEApplication(attachment.read(), _subtype=sub_type)
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_path)
            message.attach(attachment)

    # Convertir le message en une chaîne encodée en base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Envoyer l'e-mail via l'API Gmail
    try:
        sent_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print('Message Id: %s' % sent_message['id'])
    except Exception as error:
        print(f'An error occurred: {error}')

