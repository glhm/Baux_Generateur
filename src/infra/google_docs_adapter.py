# infrastructure/google_docs_adapter.py
from application.ports.document_editing_port import DocumentEditingPort

class GoogleDocsAdapter(DocumentEditingPort):
    def __init__(self, docs_service):
        self.docs_service = docs_service

    def update_placeholders(self, document_id: str, replacements: dict):
        replace_requests = [
            {
                "replaceAllText": {
                    "containsText": {"text": f"{{{{{k}}}}}", "matchCase": True},
                    "replaceText": v
                }
            }
            for k, v in replacements.items()
        ]
        self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': replace_requests}).execute()
        print(f"[INFO] Placeholders mis à jour pour le document: {document_id}")
