# application/ports/document_storage_port.py
from abc import ABC, abstractmethod

class DocumentStoragePort(ABC):
    @abstractmethod
    def copy_file(self, template_id: str, new_name: str) -> str:
        """Copie un modèle et retourne l'ID du nouveau document"""
        pass

    @abstractmethod
    def export_pdf(self, document_id: str, folder_id: str, file_name: str):
        """Exporte le document en PDF dans un dossier cible"""
        pass

    @abstractmethod
    def delete_file(self, document_id: str):
        """Supprime le document"""
        pass
