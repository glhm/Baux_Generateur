import io
import os
import pickle
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'
          , 'https://www.googleapis.com/auth/gmail.send']


def authenticate_and_create_services():
    """Authenticate and create Google API services."""
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Lire le contenu du JSON depuis la variable d'environnement
            client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
            if client_secret_json is None:
                raise ValueError("La variable d'environnement 'GOOGLE_CLIENT_SECRET_JSON' n'est pas définie.")

            # Charger les informations de client_secret depuis le JSON
            client_secret_info = json.loads(client_secret_json)
            flow = InstalledAppFlow.from_client_config(client_secret_info, SCOPES)
            
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


def get_or_create_year_folder(drive_service, parent_folder_id, year):
    """
    Récupère ou crée un dossier pour l'année spécifiée dans le dossier parent.
    
    :param drive_service: Service Google Drive.
    :param parent_folder_id: ID du dossier parent (Locatif).
    :param year: Année pour laquelle créer le dossier.
    :return: ID du dossier de l'année.
    """
    # Rechercher si le dossier existe déjà
    query = f"'{parent_folder_id}' in parents and name = '{year}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        print(f"[INFO] Dossier pour l'année {year} trouvé: {files[0]['id']}")
        return files[0]['id']
    
    # Créer le dossier s'il n'existe pas
    file_metadata = {
        'name': year,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    
    try:
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"[INFO] Dossier pour l'année {year} créé: {folder['id']}")
        return folder['id']
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création du dossier pour l'année {year}: {e}")
        return None


def get_or_create_subfolder(drive_service, parent_folder_id, folder_name):
    """
    Récupère ou crée un sous-dossier dans le dossier parent.
    
    :param drive_service: Service Google Drive.
    :param parent_folder_id: ID du dossier parent.
    :param folder_name: Nom du sous-dossier à créer ou récupérer.
    :return: ID du sous-dossier.
    """
    # Rechercher si le dossier existe déjà
    query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        print(f"[INFO] Sous-dossier '{folder_name}' trouvé: {files[0]['id']}")
        return files[0]['id']
    
    # Créer le dossier s'il n'existe pas
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    
    try:
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"[INFO] Sous-dossier '{folder_name}' créé: {folder['id']}")
        return folder['id']
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création du sous-dossier '{folder_name}': {e}")
        return None


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

def create_and_export_doc_from_template(template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service):
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

        import re

def delete_files_matching_regex(drive_service, folder_id, pattern):
    """Supprime tous les fichiers dans un dossier Google Drive qui correspondent à un motif regex, avec gestion des erreurs."""
    query = f"'{folder_id}' in parents and trashed = false"  # Rechercher dans le dossier sans fichiers dans la corbeille
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        # Filtrer les fichiers qui correspondent à la regex
        matching_files = [file for file in files if pattern.match(file['name'])]
        
        if matching_files:
            for file in matching_files:
                try:
                    file_id = file['id']
                    print(f"[INFO] Suppression du fichier correspondant : {file['name']}")
                    drive_service.files().delete(fileId=file_id).execute()
                    print(f"[INFO] Fichier supprimé : {file['name']}")
                except HttpError as error:
                    print(f"[ERROR] Une erreur s'est produite lors de la suppression du fichier {file['name']}: {error}")
        else:
            print("[INFO] Aucun fichier correspondant à la regex n'a été trouvé.")
    
    except HttpError as error:
        print(f"[ERROR] Une erreur s'est produite lors de la récupération des fichiers : {error}")
