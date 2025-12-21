from src.domain.ports.services import NotificationService
from src.infrastructure.adapters.google_client import GoogleClient
from src.domain.exceptions.custom_exceptions import InfrastructureException
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailAdapter(NotificationService):
    def __init__(self):
        _, _, self.gmail_service = GoogleClient.get_services()

    def send_email(self, recipient: str, subject: str, body: str, attachments: list[str] = []) -> None:
        try:
            message = MIMEMultipart()
            message['to'] = recipient
            message['subject'] = subject
            
            msg = MIMEText(body)
            message.attach(msg)
            
            # Attachments logic would go here (reading files, encoding base64)
            # Skipping implementation for brevity
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw}
            
            self.gmail_service.users().messages().send(userId='me', body=body).execute()
        
        except Exception as e:
            raise InfrastructureException(f"Gmail Error: {e}")
