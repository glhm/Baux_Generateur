import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.adapters.google_auth_provider import GoogleAuthProvider
from src.ports.mail_port import MailPort

class GmailAdapter(MailPort):
    """Adapter for Gmail API operations."""
    
    def __init__(self, auth_provider: GoogleAuthProvider):
        creds = auth_provider.get_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
        
    def send_email_with_attachment(self, to_address: str, subject: str, body: str, attachment_name: str, attachment_data: bytes) -> dict:
        """
        Send an email with a PDF attachment.
        Returns the sent message object or None on failure.
        """
        try:
            message = MIMEMultipart()
            message['to'] = to_address
            message['subject'] = subject
            
            msg = MIMEText(body)
            message.attach(msg)
            
            if attachment_data:
                part = MIMEBase('application', 'pdf')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
                message.attach(part)
                
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            body = {'raw': raw_message}
            
            sent_message = self.service.users().messages().send(userId='me', body=body).execute()
            print(f"[INFO] Email envoyé à {to_address} (ID: {sent_message['id']})")
            return sent_message
            
        except HttpError as error:
            print(f"[ERROR] Une erreur s'est produite lors de l'envoi de l'email : {error}")
            return None
