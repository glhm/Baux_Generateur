import io
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from my_secrets.notion_secrets import CLIENT_GOOGLE_SECRET_JSON_PATH  # Importez le chemin vers le fichier de secrets

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'
          , 'https://www.googleapis.com/auth/gmail.send']

def authenticate_and_create_services():

    # Authentification et création des services
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_GOOGLE_SECRET_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)

    return drive_service, docs_service, gmail_service

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
    # Supprimer l'ancien fichier s'il existe
    delete_existing_file_if_exists(drive_service, file_name, folder_id)

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


def find_file_in_folder(folder_id, file_name, drive_service):
    """Trouve un fichier par son nom dans un dossier spécifique"""
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print(f"Le fichier '{file_name}' n'a pas été trouvé dans le dossier.")
        return None
    return files[0]['id']

def download_file_from_drive(file_id, drive_service):
    """Télécharge un fichier depuis Google Drive et renvoie son contenu sous forme de flux en mémoire"""
    request = drive_service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"[INFO] Téléchargement {int(status.progress() * 100)}% terminé.")
    file_stream.seek(0)
    return file_stream

def delete_existing_file_if_exists(drive_service, file_name, folder_id):
    """Supprime un fichier existant dans Google Drive avec le même nom"""
    query = f"name='{file_name}' and '{folder_id}' in parents"
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        for file in files:
            file_id = file['id']
            print(f"[INFO] Suppression du fichier existant : {file['name']}")
            drive_service.files().delete(fileId=file_id).execute()
            print(f"[INFO] Fichier supprimé : {file_id}")

    except HttpError as error:
        print(f"[ERROR] Une erreur s'est produite lors de la suppression du fichier : {error}")


def delete_file_by_id(file_id, drive_service):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        print(f"Fichier avec l'ID {file_id} supprimé avec succès.")
    except Exception as e:
        print(f"[ERROR] Une erreur est survenue lors de la suppression du fichier avec l'ID {file_id}: {e}")

def process_document(template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service):
    """
    Copie un modèle Google Docs, remplace les champs, exporte en PDF et supprime le fichier du Drive.

    Args:
    - template_id (str): ID du modèle à copier.
    - new_document_name (str): Nom du nouveau document.
    - replace_requests (list): Liste des requêtes pour remplacer les champs dans le document.
    - output_dir (str): Répertoire où le PDF sera sauvegardé.
    - drive_service (googleapiclient.discovery.Resource): Service Google Drive.
    - docs_service (googleapiclient.discovery.Resource): Service Google Docs.
    """

    try:
        # Copier le modèle
        copied_file = drive_service.files().copy(fileId=template_id, body={"name": new_document_name}).execute()
        document_id = copied_file['id']
        print(f"[INFO] Modèle copié avec succès. {new_document_name}")

        # Mettre à jour les champs du document
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': replace_requests}).execute()
        print(f"[INFO] Champs remplacés pour {new_document_name}.")

        # Exporter le document au format PDF
        export_doc_to_pdf_and_upload(document_id, drive_service, folder_id, new_document_name)

        # Supprimer le fichier du Drive après exportation
        delete_file_by_id(document_id, drive_service)

    except Exception as e:
        print(f"[ERROR] Une erreur est survenue lors du traitement du document {new_document_name}: {e}")