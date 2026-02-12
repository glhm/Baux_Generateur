from abc import ABC, abstractmethod

from typing import List, Optional

class MailPort(ABC):

    @abstractmethod

    def send_mail(self, recipient: str, subject: str, body: str, attachments: Optional[List[str]] = None):

        """Sends an email."""
        pass

