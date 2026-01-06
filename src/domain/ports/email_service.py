from abc import ABC, abstractmethod
from typing import List, Optional

class EmailService(ABC):
    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str, attachments: Optional[List[str]] = None):
        """Sends an email."""
        pass
