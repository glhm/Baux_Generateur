import os
import pickle
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send']

class GoogleClient:
    _creds = None
    _drive_service = None
    _docs_service = None
    _gmail_service = None

    @classmethod
    def get_services(cls):
        if cls._creds and cls._creds.valid:
            if not cls._drive_service:
                cls._init_services()
            return cls._drive_service, cls._docs_service, cls._gmail_service
            
        # Authenticate
        cls._authenticate()
        cls._init_services()
        return cls._drive_service, cls._docs_service, cls._gmail_service

    @classmethod
    def _authenticate(cls):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                try:
                    creds = pickle.load(token)
                except Exception:
                    pass # Invalid pickle

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
                if not client_secret_json:
                     # Fallback to file if env var not set (legacy support)
                     if os.path.exists('credentials.json'):
                         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                     else:
                        raise ValueError("GOOGLE_CLIENT_SECRET_JSON env var or credentials.json not found.")
                else:
                    client_secret_info = json.loads(client_secret_json)
                    flow = InstalledAppFlow.from_client_config(client_secret_info, SCOPES)
                
                # Note: run_local_server requires a browser, which won't work in Lambda or headless.
                # In Lambda, we must rely on a valid token.pickle or stored refresh token.
                # For this Local tool run, it's fine.
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        cls._creds = creds

    @classmethod
    def _init_services(cls):
        cls._drive_service = build('drive', 'v3', credentials=cls._creds)
        cls._docs_service = build('docs', 'v1', credentials=cls._creds)
        cls._gmail_service = build('gmail', 'v1', credentials=cls._creds)
