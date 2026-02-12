import os
import pickle
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]


class GoogleAuthProvider:
    """
    Shared OAuth2 authentication provider for all Google API adapters.
    Authenticates once and exposes credentials for service construction.
    """

    def __init__(self):
        self._creds = self._authenticate()

    def get_credentials(self):
        return self._creds

    def _authenticate(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
                if client_secret_json is None:
                    raise ValueError("La variable d'environnement 'GOOGLE_CLIENT_SECRET_JSON' n'est pas définie.")

                client_secret_info = json.loads(client_secret_json)
                flow = InstalledAppFlow.from_client_config(client_secret_info, SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

        return creds
