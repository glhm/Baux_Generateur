
import io
from googleapiclient.http import MediaIoBaseDownload

def export_doc_to_pdf(doc_id, document_name,drive_service):
    print(f"[INFO] Exportation du document {document_name} au format PDF...")
    request = drive_service.files().export_media(fileId=doc_id, mimeType='application/pdf')
    pdf_filename = f'{document_name}.pdf'
    with io.FileIO(pdf_filename, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloaded {int(status.progress() * 100)}% for {pdf_filename}.")

    print(f"[INFO] Exportation de {pdf_filename} terminée.")

def delete_file_by_name(service, file_name):
    """Supprime un fichier de Google Drive en utilisant son nom."""
    
    results = service.files().list(q=f"name='{file_name}'", spaces='drive').execute()
    items = results.get('files', [])

    if not items:
        print(f"[INFO] Aucun fichier nommé {file_name} trouvé.")
        return

    # Si plusieurs fichiers portent le même nom, tous seront supprimés.
    for item in items:
        print(f"[INFO] Suppression du fichier {item['name']} (ID: {item['id']})")
        service.files().delete(fileId=item['id']).execute()
        print(f"[INFO] Fichier {item['name']} supprimé avec succès.")