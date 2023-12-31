import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from notion_database import *
from google_doc import *
from datetime import datetime
from googlemail import *
import locale

from my_secrets.notion_secrets import CLIENT_GOOGLE_SECRET_JSON_PATH

annee_courante = datetime.now().year

# Définir la localisation sur "fr_FR"
locale.setlocale(locale.LC_TIME, 'fr_FR')

# Obtenir le nom du mois actuel avec des accents
current_month_with_accents = datetime.now().strftime('%B').capitalize()



SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send']

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
TEMPLATE_QUITTANCE_ID = '1r9BDMtM2h37-eIZoCz0kzzdy_z0r3-caBC6atkPo-20'

# 2. Modifiez le nouveau document
all_data = {}
retrieve_notion_datas(all_data)

for locataire in all_data['locataire']['results']:


    # Vérification de la case ActiverGeneration
    activer_generation = locataire['properties'].get('ActiverGeneration', {}).get('checkbox', False)
    activer_generation_quittance = locataire['properties'].get('ActiverGenerationQuittances', {}).get('checkbox', False)
    envoyer_quittance = locataire['properties'].get('EnvoyerQuittance', {}).get('checkbox', False)

    if not activer_generation and not activer_generation_quittance and not envoyer_quittance:
        continue  # Si la case n'est pas cochée, on passe au locataire suivant

    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    print(f"Nouveau locataire {locataire_name}")
    formatted_name = locataire_name.replace(" ", "_").replace("'", "_")

    # Remplacer les champs du modèle par les données du locataire actuel

    chambre_dict = {}
    garant_dict = {}
    bien_dict = {}
    locataire_dict,info_rollup = extract_fields_from_locataire_database(locataire)
    print(locataire_dict)


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

    if activer_generation :
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
        docs_service.documents().batchUpdate(documentId=NEW_DOCUMENT_ID, body={'requests': all_replace_requests}).execute()
        print(f"[INFO] Champs remplacés pour {new_document_name}.")
        docs_service.documents().batchUpdate(documentId=NEW_CAUTION_ID, body={'requests': all_replace_requests}).execute()
        print(f"[INFO] Champs remplacés pour {new_caution_doc_name}.")

        #Exporter le document modifié au format PDF
        export_doc_to_pdf(NEW_DOCUMENT_ID, new_document_name,drive_service)
        export_doc_to_pdf(NEW_CAUTION_ID, new_caution_doc_name,drive_service)

    if activer_generation_quittance :
        map_jour = [
            {"Janvier": "31"}
            ,{"Février": "28"},
            {"Mars": "31"},
            {"Avril": "30"},
            {"Mai": "31"},
            {"Juin": "30"},
            {"Juillet": "31"},
            {"Août": "31"},
            {"Septembre": "30"},
            {"Octobre": "31"},
            {"Novembre": "30"},
            {"Décembre": "31"}       
        ]

        for month_dict in map_jour:
            key, value = list(month_dict.items())[0]
            all_replace_requests.extend(add_one_request("{{MOIS_COURANT}}",key))
            all_replace_requests.extend(add_one_request("{{DERNIER_JOUR}}",value))

            all_replace_requests.extend(add_one_request("{{ANNEE_COURANTE}}",annee_courante ))
            new_quittance_doc_name = f"Quittance_de_loyer_{formatted_name}_{key}_{annee_courante}"
            delete_file_by_name(drive_service, new_quittance_doc_name)

            copied_file = drive_service.files().copy(fileId=TEMPLATE_QUITTANCE_ID, body={"name": new_quittance_doc_name}).execute()
            print(f"[INFO] Modèle copié avec succès. {new_quittance_doc_name}")
            NEW_DOCUMENT_ID = copied_file['id']

            docs_service.documents().batchUpdate(documentId=NEW_DOCUMENT_ID, body={'requests': all_replace_requests}).execute()
            print(f"[INFO] Champs remplacés pour {new_quittance_doc_name}.")

            #Exporter le document modifié au format PDF
            export_doc_to_pdf(NEW_DOCUMENT_ID, new_quittance_doc_name,drive_service)

    if envoyer_quittance :
        # Utilisation de la fonction send_email
        to_address = mail_value = locataire['properties']['Mail']['rich_text'][0]['text']['content']
        print(f'Locataire dict {locataire}')
        subject = f'Quittance de loyer {current_month_with_accents} {annee_courante}'
        body = 'Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault'
        nom_fichier = f"Quittance_de_loyer_{formatted_name}_{current_month_with_accents}_{annee_courante}.pdf" 
        attachment_path = f'D:\\Guilhem\\Documents\\documents immo\\\Quittances_a_envoyer\\{nom_fichier}'

    # # Vérifier si le fichier existe
    # if os.path.exists(attachment_path):
    #     # Le fichier existe, alors appeler la fonction send_email
    #     print(f"Quittance à envoyer existe, Envoi mail à l'adresse {to_address}.\n Sujet : {subject} \n body : {body}\n attachment_path : {attachment_path}")
    #     send_email(to_address, subject, body, attachment_path)
    # else:
    #     # Le fichier n'existe pas, afficher un message ou prendre une autre action si nécessaire
    #     print(f"Le fichier {nom_fichier} n'existe pas.")

        send_email(to_address, subject, body,'')


