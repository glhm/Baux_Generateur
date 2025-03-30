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