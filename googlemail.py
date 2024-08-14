from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import mimetypes

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError  

def send_email_with_attachment(to_address, subject, body, attachment_stream, attachment_name, gmail_service):
    """Envoie un e-mail avec une pièce jointe en utilisant un flux en mémoire"""
    
    # Créer un message MIME multipart pour inclure le corps et la pièce jointe
    message = MIMEMultipart()
    message['From'] = 'me'
    message['To'] = to_address
    message['Subject'] = subject
    
    # Ajouter le corps du message
    message.attach(MIMEText(body, 'plain'))
    
    # Ajouter la pièce jointe
    if attachment_stream:
        attachment = MIMEApplication(attachment_stream.read(), _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        message.attach(attachment)

    # Encoder le message au format base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        # Envoyer l'email en utilisant l'API Gmail
        sent_message = gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"[INFO] E-mail envoyé avec succès. Message ID: {sent_message['id']}")
    except HttpError as error:
        print(f"[ERROR] Une erreur s'est produite lors de l'envoi de l'e-mail : {error}")


