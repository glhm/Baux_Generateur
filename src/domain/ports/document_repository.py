from abc import ABC, abstractmethod

from src.domain.entities.document import Document


class DocumentPort(ABC):

    @abstractmethod

    def save_document(self, document: Document, folder_id: str) -> str:
        """

        Saves a document (e.g., creates it in Google Docs).

        Returns the ID or path of the saved document.
        """

        pass

