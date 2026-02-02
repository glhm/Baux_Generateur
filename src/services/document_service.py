# application/services/document_service.py
from domain.document import Document
from application.ports.document_storage_port import DocumentStoragePort
from application.ports.document_editing_port import DocumentEditingPort

class DocumentService:
    """
    Service qui orchestre la génération de documents.
    Ne connaît rien à Google, Word ou autre API.
    """
    def __init__(self, storage: DocumentStoragePort, editor: DocumentEditingPort):
        self.storage = storage
        self.editor = editor

    def generate_document(self, document: Document, folder_id: str) -> str:
        # Copier le modèle
        document_id = self.storage.copy_file(document.template_id, document.name)

        # Mettre à jour les placeholders
        self.editor.update_placeholders(document_id, document.replacements)

        # Exporter le document en PDF
        self.storage.export_pdf(document_id, folder_id, document.name)

        # Supprimer le document temporaire
        self.storage.delete_file(document_id)

        return document_id
