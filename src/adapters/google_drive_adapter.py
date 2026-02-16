import io
import re
from typing import Optional, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from src.adapters.google_auth_provider import GoogleAuthProvider

class GoogleDriveAdapter:
    """Adapter for Google Drive API operations."""
    
    def __init__(self, auth_provider: GoogleAuthProvider):
        creds = auth_provider.get_credentials()
        self.service = build('drive', 'v3', credentials=creds)

    def find_receipt_in_folder(self, folder_id: str, pattern: re.Pattern) -> Optional[dict]:
        """
        Search for a file matching the regex pattern in the specified folder.
        Returns check dict {'id': file_id, 'name': file_name} or None.
        Raises error if multiple matches found.
        """
        query = f"'{folder_id}' in parents and mimeType = 'application/pdf' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        matching_files = [f for f in files if pattern.match(f['name'])]
        
        if len(matching_files) == 0:
            return None
        if len(matching_files) > 1:
            raise ValueError(f"Plusieurs fichiers trouvés correspondant au motif dans le dossier {folder_id}")
            
        return matching_files[0]

    def download_file(self, file_id: str) -> bytes:
        """Download file content as bytes."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()
        

    def delete_files_matching_regex(self, folder_id: str, pattern: re.Pattern) -> None:
        """Delete all non-trashed files in folder that match a regex pattern."""
        query = f"'{folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        for file_data in files:
            if pattern.match(file_data['name']):
                self.service.files().delete(fileId=file_data['id']).execute()

    def get_subfolder_id(self, parent_id: str, folder_name: str) -> Optional[str]:
        """Find subfolder by name."""
        query = f"'{parent_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None

    def create_subfolder(self, parent_id: str, folder_name: str) -> str:
        """Create subfolder."""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']

    def get_or_create_subfolder(self, parent_id: str, folder_name: str) -> str:
        fid = self.get_subfolder_id(parent_id, folder_name)
        if fid:
            return fid
        return self.create_subfolder(parent_id, folder_name)
