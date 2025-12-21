from abc import ABC, abstractmethod
from src.domain.entities.document import Document
from src.domain.entities.tenant import Tenant

class DocumentService(ABC):
    @abstractmethod
    def generate_document(self, document: Document) -> str:
        """Generates a document and returns its URL or path."""
        pass

    @abstractmethod
    def download_document_as_pdf(self, document_id: str) -> str:
        """Downloads a document as PDF and returns the local path."""
        pass

class NotificationService(ABC):
    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str, attachments: list[str] = []) -> None:
        pass

class LoggerPort(ABC):
    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str, exc_info: bool = False):
        pass

    @abstractmethod
    def warning(self, message: str):
        pass
