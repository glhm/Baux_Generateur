from typing import Dict
from src.domain.ports.document_repository import DocumentRepository
from src.domain.entities.document import Document
# reusing existing service logic for auth and low-level calls if desirable,
# or reimplementing using the authenticated services.
from src.services.google_doc_and_drive_service import (
    authenticate_and_create_services,
    create_and_export_doc_from_template
)

class GoogleDriveAdapter(DocumentRepository):
    def __init__(self):
        self.drive_service, self.docs_service, self.gmail_service = authenticate_and_create_services()

    def save_document(self, document: Document, folder_id: str) -> str:
        """
        Creates a document from a template, replaces placeholders, and exports it.
        """
        # Convert Dictionary[str, str] to the structure expected by the Google API helper
        # helper expects a list of requests: [{'replaceAllText': ...}, ...]
        # We should probably move the `build_replace_requests_from_dict` logic here or to the helper?
        # The prompt said "The mechanic which consisted of replacing placeholders directly thanks to their column name is deleted now we build the placeholder dictionary in a separate service".
        # So `document.replacements` is ready to be used.
        
        replace_requests = self._build_requests(document.replacements)
        
        # Call the existing service function (which eventually we might refactor fully into this adapter)
        # Note: create_and_export_doc_from_template handles copy, update, export, delete temp.
        # It returns None currently but prints. We might want it to return the PDF ID.
        # For now, let's assume it works as side-effect.
        
        create_and_export_doc_from_template(
            template_id=document.template_id,
            new_document_name=document.name,
            replace_requests=replace_requests,
            folder_id=folder_id,
            drive_service=self.drive_service,
            docs_service=self.docs_service
        )
        
        return "Document processed" # Todo: return actual ID if refactored

    def _build_requests(self, replacements: Dict[str, str]):
        requests = []
        for key, value in replacements.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': key, # Key should already include braces if needed, or we add them?
                        # User said: "mechanic ... replacing placeholders directly thanks to their column name is deleted".
                        # PlaceholderService should provide exact keys e.g. "{{NOM}}".
                        'matchCase': True,
                    },
                    'replaceText': value,
                }
            })
        return requests
