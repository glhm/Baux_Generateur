
import io
import os 
from googleapiclient.http import MediaIoBaseDownload,MediaIoBaseUpload

def export_doc_to_pdf(document_id, document_name, drive_service, output_path):
    request = drive_service.files().export_media(fileId=document_id, mimeType='application/pdf')
    file_path = os.path.join(output_path, f'{document_name}.pdf')
    with open(file_path, 'wb') as pdf_file:
        pdf_file.write(request.execute())
    print(f"[INFO] Document exporté en PDF: {file_path}")

def export_doc_to_pdf_and_upload(doc_id, drive_service, folder_id, file_name):
    # Exporter le document en PDF et obtenir les données du PDF en mémoire
    request = drive_service.files().export_media(fileId=doc_id, mimeType='application/pdf')
    file_stream = io.BytesIO()
    
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"[INFO] Exportation {int(status.progress() * 100)}% terminée.")
    
    # Repositionner le curseur du stream au début
    file_stream.seek(0)

    # Uploader le fichier PDF dans le dossier spécifique sur Google Drive
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'mimeType': 'application/pdf'
    }
    media = MediaIoBaseUpload(file_stream, mimetype='application/pdf')

    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"[INFO] Fichier PDF uploadé avec succès. ID : {uploaded_file.get('id')}")


def delete_file_by_name(service, file_name):
    #Supprime un fichier de Google Drive en utilisant son nom.
    
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

def delete_file_by_id(file_id, drive_service):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        print(f"[INFO] Fichier avec l'ID {file_id} supprimé avec succès.")
    except Exception as e:
        print(f"[ERROR] Une erreur est survenue lors de la suppression du fichier avec l'ID {file_id}: {e}")