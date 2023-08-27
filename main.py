import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from notion_database import *
from google_doc import *
from my_secrets.notion_secrets import CLIENT_GOOGLE_SECRET_JSON_PATH


SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

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

# ID du modèle Google Doc
TEMPLATE_ID = '1JUeo7xhqobGXFKTejKc1O3wgo4RU0mZKqKSvBmhLnjw'
CAUTION_ID = '1mtoeS2JrLf9eW6d4sfJZyEKXzPYIrNn6PcChAcgfmqI'

# 2. Modifiez le nouveau document
all_data = {}
retrieve_notion_datas(all_data)

for locataire in all_data['locataire']['results']:

    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    print(f"Nouveau locataire {locataire_name}")
    formatted_name = locataire_name.replace(" ", "_").replace("'", "_")

    new_document_name = f"bail_location_{formatted_name}"
    new_caution_doc_name = f"Acte_de_caution_solidaire_{formatted_name}"

           # print(locataire)  
    delete_file_by_name(drive_service, new_document_name)
    delete_file_by_name(drive_service, new_caution_doc_name)


    copied_file = drive_service.files().copy(fileId=TEMPLATE_ID, body={"name": new_document_name}).execute()
    print(f"[INFO] Modèle copié avec succès. {new_document_name}")
    NEW_DOCUMENT_ID = copied_file['id']

    copied_file = drive_service.files().copy(fileId=CAUTION_ID, body={"name": new_caution_doc_name}).execute()
    print(f"[INFO] Modèle copié avec succès. {new_caution_doc_name}")
    NEW_CAUTION_ID = copied_file['id']
    # Remplacer les champs du modèle par les données du locataire actuel

    locataire_dict,info_rollup = extract_fields_from_locataire_database(locataire)
    print(locataire_dict)
    chambre_dict = {}
    garant_dict = {}
    bien_dict = {}

    guarantor_id = info_rollup.get('guarantor_id')
    if guarantor_id:
        for garant in all_data['garants']['results']:
            if garant['id'] == guarantor_id:
                garant_dict = extract_fields_from_database(garant)
                print(garant_dict)
     
    bien_id = info_rollup.get('bien_id')
    if bien_id:
        for bien in all_data['bien']['results']:
            if bien['id'] == bien_id:
                bien_dict = extract_fields_from_database(bien)
                print(bien_dict)

    chambre_id = info_rollup.get('chambre_id')
    if chambre_id:
        for chambre in all_data['chambres']['results']:
            if chambre['id'] == chambre_id:
                chambre_dict = extract_fields_from_database(chambre)
                print(chambre_dict)

all_replace_requests = []
all_replace_requests.extend(build_replace_requests(locataire_dict))
if guarantor_id:
    all_replace_requests.extend(build_replace_requests(garant_dict))
if bien_id:
    all_replace_requests.extend(build_replace_requests(bien_dict))
if chambre_id:
    all_replace_requests.extend(build_replace_requests(chambre_dict))

print(all_replace_requests)
docs_service.documents().batchUpdate(documentId=NEW_DOCUMENT_ID, body={'requests': all_replace_requests}).execute()
print(f"[INFO] Champs remplacés pour {new_document_name}.")
docs_service.documents().batchUpdate(documentId=NEW_CAUTION_ID, body={'requests': all_replace_requests}).execute()
print(f"[INFO] Champs remplacés pour {new_caution_doc_name}.")

#Exporter le document modifié au format PDF
export_doc_to_pdf(NEW_DOCUMENT_ID, new_document_name,drive_service)
export_doc_to_pdf(NEW_CAUTION_ID, new_caution_doc_name,drive_service)