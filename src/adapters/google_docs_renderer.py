import io
from typing import Dict

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

from src.ports.template_renderer_port import TemplateRenderer
from src.adapters.google_auth_provider import GoogleAuthProvider


class GoogleDocsRenderer(TemplateRenderer):

    def __init__(self, auth_provider: GoogleAuthProvider):
        creds = auth_provider.get_credentials()
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)

    # ── TemplateRenderer implementation ─────────────────────────────

    def render(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        output_name: str,
        folder_id: str = None
    ) -> str:
        """
        Copies the template, replaces all placeholders, exports to PDF,
        uploads it to the target folder, and cleans up the temporary doc.
        """
        try:
            # 1. Copy template
            copied_file = self.drive_service.files().copy(
                fileId=template_id,
                body={"name": output_name}
            ).execute()
            document_id = copied_file['id']
            print(f"[INFO] Modèle copié avec succès. {output_name}")

            # 2. Replace placeholders
            replace_requests = self._build_requests(placeholders)
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': replace_requests}
            ).execute()
            print(f"[INFO] Champs remplacés pour {output_name}.")

            # 3. Export to PDF and upload
            if folder_id:
                self._export_pdf_and_upload(document_id, folder_id, output_name)

            # 4. Delete temporary Google Doc
            self._delete_file_by_id(document_id)

            return document_id

        except Exception as e:
            print(f"[ERROR] Une erreur est survenue lors du traitement du document {output_name}: {e}")
            return ""

    # ── PDF Export ──────────────────────────────────────────────────

    def export_doc_to_pdf(self, document_id: str, document_name: str, output_path: str):
        """Export a Google Doc to a local PDF file."""
        import os
        request = self.drive_service.files().export_media(fileId=document_id, mimeType='application/pdf')
        file_path = os.path.join(output_path, f'{document_name}.pdf')
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(request.execute())
        print(f"[INFO] Document exporté en PDF: {file_path}")

    def _export_pdf_and_upload(self, doc_id: str, folder_id: str, file_name: str):
        """Export a Google Doc to PDF in memory and upload to a Drive folder."""
        request = self.drive_service.files().export_media(fileId=doc_id, mimeType='application/pdf')
        file_stream = io.BytesIO()

        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"[INFO] Exportation {int(status.progress() * 100)}% terminée.")

        file_stream.seek(0)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
            'mimeType': 'application/pdf'
        }
        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf')
        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"[INFO] Fichier PDF uploadé avec succès.")

    # ── File Operations ─────────────────────────────────────────────

    def delete_file_by_name(self, file_name: str):
        """Delete file(s) from Google Drive by name."""
        results = self.drive_service.files().list(q=f"name='{file_name}'", spaces='drive').execute()
        items = results.get('files', [])

        if not items:
            print(f"[INFO] Aucun fichier nommé {file_name} trouvé.")
            return

        for item in items:
            print(f"[INFO] Suppression du fichier {item['name']} (ID: {item['id']})")
            self.drive_service.files().delete(fileId=item['id']).execute()
            print(f"[INFO] Fichier {file_name} supprimé avec succès.")

    def _delete_file_by_id(self, file_id: str):
        """Delete a file from Google Drive by its ID."""
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
        except Exception as e:
            print(f"[ERROR] Une erreur est survenue lors de la suppression du fichier avec l'ID {file_id}: {e}")

    def delete_existing_file_if_exists(self, file_name: str, folder_id: str):
        """Delete existing file with same name in a folder."""
        query = f"name='{file_name}' and '{folder_id}' in parents"
        try:
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            for file in files:
                print(f"[INFO] Suppression du fichier existant : {file['name']}")
                self.drive_service.files().delete(fileId=file['id']).execute()
                print(f"[INFO] Fichier supprimé : {file_name}")
        except HttpError as error:
            print(f"[ERROR] Une erreur s'est produite lors de la suppression du fichier : {error}")

    def find_file_in_folder(self, folder_id: str, file_name: str) -> str:
        """Find a file by name in a specific folder."""
        query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            print(f"Le fichier '{file_name}' n'a pas été trouvé dans le dossier.")
            return None
        return files[0]['id']

    def download_file(self, file_id: str) -> io.BytesIO:
        """Download a file from Google Drive, returns an in-memory stream."""
        request = self.drive_service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"[INFO] Téléchargement {int(status.progress() * 100)}% terminé.")
        file_stream.seek(0)
        return file_stream

    def delete_files_matching_regex(self, folder_id: str, pattern):
        """Delete all files in a Drive folder matching a regex pattern."""
        query = f"'{folder_id}' in parents and trashed = false"
        try:
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])

            matching_files = [file for file in files if pattern.match(file['name'])]

            if matching_files:
                for file in matching_files:
                    try:
                        print(f"[INFO] Suppression du fichier correspondant : {file['name']}")
                        self.drive_service.files().delete(fileId=file['id']).execute()
                        print(f"[INFO] Fichier supprimé : {file['name']}")
                    except HttpError as error:
                        print(f"[ERROR] Une erreur s'est produite lors de la suppression du fichier {file['name']}: {error}")
            else:
                print("[INFO] Aucun fichier correspondant à la regex n'a été trouvé.")
        except HttpError as error:
            print(f"[ERROR] Une erreur s'est produite lors de la récupération des fichiers : {error}")

    # ── Folder Operations ───────────────────────────────────────────

    def get_or_create_year_folder(self, parent_folder_id: str, year: str) -> str:
        """Get or create a year folder inside a parent folder."""
        query = f"'{parent_folder_id}' in parents and name = '{year}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            print(f"[INFO] Dossier pour l'année {year} trouvé: ")
            return files[0]['id']

        file_metadata = {
            'name': year,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        try:
            folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
            print(f"[INFO] Dossier pour l'année {year} créé")
            return folder['id']
        except Exception as e:
            print(f"[ERROR] Erreur lors de la création du dossier pour l'année {year}: {e}")
            return None

    def get_or_create_subfolder(self, parent_folder_id: str, folder_name: str) -> str:
        """Get or create a subfolder inside a parent folder."""
        query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            print(f"[INFO] Sous-dossier '{folder_name}' trouvé: {files[0]['id']}")
            return files[0]['id']

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        try:
            folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
            print(f"[INFO] Sous-dossier '{folder_name}' créé: {folder['id']}")
            return folder['id']
        except Exception as e:
            print(f"[ERROR] Erreur lors de la création du sous-dossier '{folder_name}': {e}")
            return None

    # ── Private helpers ─────────────────────────────────────────────

    def _build_requests(self, placeholders: Dict[str, str]):
        """Build Google Docs batchUpdate replace requests from a placeholder dict."""
        requests = []
        for key, value in placeholders.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': key,
                        'matchCase': True,
                    },
                    'replaceText': value,
                }
            })
        return requests
