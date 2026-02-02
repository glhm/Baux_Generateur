# infrastructure/google_drive_adapter.py
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from application.ports.document_storage_port import DocumentStoragePort

class GoogleDriveAdapter(DocumentStoragePort):
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def copy_file(self, template_id: str, new_name: str) -> str:
        copied_file = self.drive_service.files().copy(fileId=template_id, body={"name": new_name}).execute()
        print(f"[INFO] Modèle copié avec succès: {new_name} (ID: {copied_file['id']})")
        return copied_file['id']

    def export_pdf(self, document_id: str, folder_id: str, file_name: str):
        request = self.drive_service.files().export_media(fileId=document_id, mimeType='application/pdf')
        file_stream = io.BytesIO()

        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"[INFO] Exportation {int(status.progress() * 100)}% terminée.")

        file_stream.seek(0)

        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf')
        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
            'mimeType': 'application/pdf'
        }

        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"[INFO] PDF uploadé avec succès: {file_name}")

    def delete_file(self, document_id: str):
        self.drive_service.files().delete(fileId=document_id).execute()
        print(f"[INFO] Document supprimé: {document_id}")
