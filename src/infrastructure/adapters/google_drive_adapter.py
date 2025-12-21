from src.domain.ports.services import DocumentService
from src.domain.entities.document import Document
from src.infrastructure.adapters.google_client import GoogleClient
from src.domain.exceptions.custom_exceptions import InfrastructureException
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

class GoogleDriveAdapter(DocumentService):
    def __init__(self):
        self.drive_service, self.docs_service, _ = GoogleClient.get_services()

    def generate_document(self, document: Document) -> str:
        """
        Creates a new doc from template, replaces text, exports to PDF, and uploads back to Drive.
        Returns the ID of the new PDF or file path.
        """
        try:
            # 1. Copy Template
            new_file_metadata = {'name': document.name}
            copied = self.drive_service.files().copy(
                fileId=document.template_id, 
                body=new_file_metadata
            ).execute()
            doc_id = copied.get('id')

            # 2. Replace Text
            # Mapping Dict[str, str] -> Google BatchUpdate Requests
            requests = []
            if document.replacements:
                for key, value in document.replacements.items():
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': key,
                                'matchCase': True
                            },
                            'replaceText': str(value)
                        }
                    })
            
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id, body={'requests': requests}
                ).execute()

            # 3. Export to PDF (optional step based on existing logic)
            return doc_id

        except Exception as e:
            raise InfrastructureException(f"Google Drive Error: {e}")

    def download_document_as_pdf(self, document_id: str) -> str:
        # Implementation of download logic
        try:
            request = self.drive_service.files().export_media(fileId=document_id, mimeType='application/pdf')
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_stream.seek(0)
            
            # Save locally
            output_path = f"/tmp/{document_id}.pdf" # /tmp for Lambda compatibility
            with open(output_path, "wb") as f:
                f.write(file_stream.read())
            
            return output_path

        except Exception as e:
             raise InfrastructureException(f"Download Error: {e}")
