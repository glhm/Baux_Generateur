import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from notion_database import *
from google_doc import *
from datetime import datetime
from googlemail import *
from mystrings import *
import locale
import os

from my_secrets.notion_secrets import CLIENT_GOOGLE_SECRET_JSON_PATH

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


# Définir la localisation sur "fr_FR"
locale.setlocale(locale.LC_TIME, 'fr_FR')

# Obtenir le nom du mois actuel avec des accents
current_month_with_accents = datetime.now().strftime('%B').capitalize()

# Chemin vers les répertoires "output/baux" et "output/quittances"
output_baux_dir = os.path.join(os.path.dirname(__file__), 'output', 'baux')
output_quittances_dir = os.path.join(os.path.dirname(__file__), 'output', 'quittances')

# Créer les répertoires s'ils n'existent pas
os.makedirs(output_baux_dir, exist_ok=True)
os.makedirs(output_quittances_dir, exist_ok=True)

print(output_baux_dir)
print(output_quittances_dir)

map_jour = {
                "Janvier": 31,
                "Février": 28,  # Attention, février peut être de 28 ou 29 jours selon l'année (non pris en compte ici)
                "Mars": 31,
                "Avril": 30,
                "Mai": 31,
                "Juin": 30,
                "Juillet": 31,
                "Août": 31,
                "Septembre": 30,
                "Octobre": 31,
                "Novembre": 30,
                "Décembre": 31
            }

mois_list = list(map_jour.keys())  # Convertir les clés du dictionnaire en liste

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'
          , 'https://www.googleapis.com/auth/gmail.send']

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

# ID du modèle Google Doc
ID_TEMPLATE_BAIL_MEUBLE = '18VYMLwkmgNauvdPfBq6tmbxvBOq0FsPXmTxav1smXAw'

CAUTION_ID = '1mtoeS2JrLf9eW6d4sfJZyEKXzPYIrNn6PcChAcgfmqI'
TEMPLATE_QUITTANCE_ID = '1r9BDMtM2h37-eIZoCz0kzzdy_z0r3-caBC6atkPo-20'
TEMPLATE_QUITTANCE_1_MOIS_ID = '1Ixo7-NVqqtTcg1lk8jl9dibKtAHA4ia5GjrlTvQDKUM'

ID_REPO_QUITTANCES = '16zx1IkNaOPAMqXddqyxwYhHBR72Twfxy'
# 2. Modifiez le nouveau document
all_data = {}
retrieve_notion_datas(all_data)

for locataire in all_data['locataire']['results']:


    # Vérification de la case ActiverGeneration
   # print(locataire['properties'])
    activer_generation = locataire['properties'].get('ActiverGeneration', {}).get('checkbox', False)
    activer_generation_quittance = locataire['properties'].get('ActiverGenerationQuittances', {}).get('checkbox', False)
    envoyer_quittance = locataire['properties'].get('EnvoyerQuittance', {}).get('checkbox', False)

    if not activer_generation and not activer_generation_quittance and not envoyer_quittance:
        continue  # Si la case n'est pas cochée, on passe au locataire suivant

    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    print(f"Nouveau locataire {locataire_name}")
    formatted_name = locataire_name.replace(" ", "_").replace("'", "_").replace(",", "")

    # Remplacer les champs du modèle par les données du locataire actuel

    chambre_dict = {}
    garant_dict = {}
    bien_dict = {}
    locataire_dict,info_rollup = extract_fields_from_locataire_database(locataire)


    guarantor_id = info_rollup.get('guarantor_id')
    if guarantor_id:
        for garant in all_data['garants']['results']:
            if garant['id'] == guarantor_id:
                garant_dict = extract_fields_from_database(garant)
                #print(garant_dict)
     
    bien_id = info_rollup.get('bien_id')
    if bien_id:
        for bien in all_data['bien']['results']:
            if bien['id'] == bien_id:
                bien_dict = extract_fields_from_database(bien)
                #print(bien_dict)

    chambre_id = info_rollup.get('chambre_id')
    if chambre_id:
        for chambre in all_data['chambres']['results']:
            if chambre['id'] == chambre_id:
                chambre_dict = extract_fields_from_database(chambre)
                #print(chambre_dict)

    # tout convertir en string
    locataire_dict_str = {key: str(value) for key, value in locataire_dict.items()}
    guarant_dict_str = {key: str(value) for key, value in garant_dict.items()}
    bien_dict_str = {key: str(value) for key, value in bien_dict.items()}
    chambre_dict_str  = {key: str(value) for key, value in chambre_dict.items()}

    all_replace_requests = []

    type_caution = locataire['properties'].get('Garantie', {}).get('select', {}).get('name', '')

    if type_caution == "Visale" :
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_visale))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", ""))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", ""))

        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", doc_visale))
    else :
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_physique))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", la_caution_physique))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", signature_des_garants))
        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", ""))


    # Ajouter les dictionnaires convertis aux demandes de remplacement
    all_replace_requests.extend(build_replace_requests(locataire_dict_str))
    if guarantor_id:
        all_replace_requests.extend(build_replace_requests(guarant_dict_str))
    if bien_id:
        all_replace_requests.extend(build_replace_requests(bien_dict_str))
    if chambre_id:
        all_replace_requests.extend(build_replace_requests(chambre_dict_str))
    #print(all_replace_requests)
    # si commence et finit par {} et que le type est un nombre on le cast en 

    # ----- partie calcul des montants et pour la quittance 1
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']  

    for chambre in all_data['chambres']['results']:
        if chambre['id'] == chambre_id:
            chambre_dict = extract_fields_from_database(chambre)
            print(chambre_dict)

    # Recherche de la chambre avec l'ID spécifié

    charges = chambre_dict['{MONTANT_CHARGES}']
    loyer = chambre_dict['{MONTANT_LOYER}']

    loyer_CC = loyer + charges 
    print("Le Loyer vaut")
    print(loyer_CC)
    dernier_jour = map_jour[mois_arrivee]
    ratio =  jour_arrivee / dernier_jour
    nombre_de_jours_premier_mois = (dernier_jour - jour_arrivee + 1 )
    prorata_total_CC =  nombre_de_jours_premier_mois * (loyer_CC) / dernier_jour
    prorata_loyer = loyer * prorata_total_CC / loyer_CC # produit en X
    prorata_charges = charges * prorata_total_CC / loyer_CC # produit en X
    total_premier_mois = prorata_total_CC+ 2* loyer # produit en X
    montant_garanties = 2*loyer
    annee_contrat = locataire['properties']['ANNEES']['multi_select'][0]['name']
    mention_speciale_loyer_data = locataire['properties'].get('MENTION_SPECIALE_LOYER', {}).get('rich_text', [])
    mention_speciale_loyer = mention_speciale_loyer_data[0]['text']['content'] if mention_speciale_loyer_data else ''   
    date_contrat = f"{jour_arrivee} {mois_arrivee} {annee_contrat}"

    #print(prorata_loyer) 
    #print(prorata_total_CC)              
    #print(prorata_charges)              
        
    all_replace_requests_quittance_premier_mois = []
    all_replace_requests.extend(add_one_request("{{TOTAL_1ER_MOIS}}", "{:.2f}".format((total_premier_mois))))
    all_replace_requests.extend(add_one_request("{{PRORATA_MOIS}}", "{:.2f}".format((prorata_total_CC)))) # doulon mais a supprimer plus tard
    
    if mention_speciale_loyer :
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", mention_speciale_loyer))
    else :
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", ""))

    all_replace_requests.extend(add_one_request("{{DATE_CONTRAT}}",date_contrat))

    all_replace_requests.extend(add_one_request("{{MOIS_ARRIVEE}}", mois_arrivee))
    all_replace_requests.extend(add_one_request("{{DERNIER_JOUR}}", str(dernier_jour)))
    all_replace_requests.extend(add_one_request("{{NOMBRE_JOURS_PREMIER_MOIS}}", str(nombre_de_jours_premier_mois)))

    all_replace_requests.extend(add_one_request("{{PRORATA_LOYER}}", "{:.2f}".format((prorata_loyer))))
    all_replace_requests.extend(add_one_request("{{PRORATA_CHARGES}}", "{:.2f}".format((prorata_charges))))
    all_replace_requests.extend(add_one_request("{{PRORATA_TOTAL_CC}}", "{:.2f}".format((prorata_total_CC))))

    all_replace_requests.extend(add_one_request("{{MONTANT_LOYER}}", str(loyer)))
    all_replace_requests.extend(add_one_request("{{MONTANT_CHARGES}}", str(charges)))
    all_replace_requests.extend(add_one_request("{{MONTANT_GARANTIES}}", str(montant_garanties)))

    all_replace_requests.extend(add_one_request("{{MONTANT_TOTAL}}", str(loyer_CC)))
    type_bail = locataire['properties'].get('TypeDeBail', {}).get('select', {}).get('name', '')
    
    if type_bail == 'Etudiant':
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_etudiant_duree))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", bail_etudiant_titre))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_etudiant))


    else:
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_meuble_duree))
        all_replace_requests.extend(add_one_request("{{MENTION_RECONDUCTION_MEUBLE}}", reconduction_meuble))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_meuble))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", str("")))
    
    if activer_generation :
        new_document_name = f"bail_location_{formatted_name}"
        #new_caution_doc_name = f"Acte_de_caution_solidaire_{formatted_name}"

        process_document(
        template_id=ID_TEMPLATE_BAIL_MEUBLE,
        new_document_name=new_document_name,
        replace_requests=all_replace_requests,
        output_dir=output_baux_dir,
        drive_service=drive_service,
        docs_service=docs_service
        )

        if type_caution == "Physique" :
            new_caution_doc_name = f"Acte_de_caution_solidaire_{formatted_name}"
            process_document(
                template_id=CAUTION_ID,
                new_document_name=new_caution_doc_name,
                replace_requests=all_replace_requests,
                output_dir=output_baux_dir,
                drive_service=drive_service,
                docs_service=docs_service
            )

    annee_selectionnees = locataire['properties']['ANNEES']['multi_select']

    print(annee_selectionnees)
    start_generation_quittances = False  # Variable pour indiquer quand commencer à générer les quittances normales

    for annee in annee_selectionnees:
        annee_courante = annee['name']
        annees_requests = []
        annees_requests.extend(add_one_request("{{ANNEE_COURANTE}}", annee_courante))

        for key, value in map_jour.items():
            all_replace_requests_month = []
            all_replace_requests_month.extend(add_one_request("{{MOIS_COURANT}}", key))
            all_replace_requests_month.extend(add_one_request("{{DERNIER_JOUR}}", str(value)))
            
            # Modifier le nom du fichier de quittance pour qu'il suive le format "Quittance_de_loyer_12_2025_Nom_Personne"

            mois_numero = mois_list.index(key) + 1  # Convertir le nom du mois en son numéro (ex: Janvier -> 1)
            mois_numero_str = f"{mois_numero:02}"  # Formater le numéro du mois sur deux chiffres (ex: 01, 02, ..., 12)
            new_quittance_doc_name = f"Quittance_de_loyer_{annee_courante}_{mois_numero_str}_{formatted_name}"

            if not start_generation_quittances:  
                # Si la génération des quittances normales n'a pas encore commencé
                if mois_arrivee != key:
                    continue  # Ignore les mois avant le mois d'arrivée
                else:
                    # Génération de la quittance du 1er mois
                    print("Generation Quittance 1er mois de loyer")
                    process_document(
                        template_id=TEMPLATE_QUITTANCE_1_MOIS_ID,
                        new_document_name=new_quittance_doc_name,
                        replace_requests=all_replace_requests + annees_requests,
                        output_dir=output_quittances_dir,
                        drive_service=drive_service,
                        docs_service=docs_service
                    )

                    # Marquer le début de la génération des quittances normales
                    start_generation_quittances = True
            else:
                # Génération des quittances normales pour tous les mois
                process_document(
                template_id=TEMPLATE_QUITTANCE_ID,
                new_document_name=new_quittance_doc_name,
                replace_requests=all_replace_requests + annees_requests + all_replace_requests_month,
                output_dir=output_quittances_dir,
                drive_service=drive_service,
                docs_service=docs_service
            )

    if envoyer_quittance :
        # Utilisation de la fonction send_email
        to_address = mail_value = locataire['properties']['Mail']['rich_text'][0]['text']['content']
        subject = f'Quittance de loyer {current_month_with_accents} {annee_courante}'
        body = 'Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault'
        nom_fichier = f"Quittance_de_loyer_{formatted_name}_{current_month_with_accents}_{annee_courante}.pdf" 
        attachment_path = f'D:\\Guilhem\\Documents\\documents immo\\\Quittances_a_envoyer\\{nom_fichier}'

        # Vérifier si le fichier existe
        if os.path.exists(attachment_path):
            # Le fichier existe, alors appeler la fonction send_email
            print(f"Quittance à envoyer existe, Envoi mail à l'adresse {to_address}.\n Sujet : {subject} \n body : {body}\n attachment_path : {attachment_path}")
            send_email(to_address, subject, body, attachment_path)
        else:
            # Le fichier n'existe pas, afficher un message ou prendre une autre action si nécessaire
            print(f"Le fichier {nom_fichier} n'existe pas.")
            send_email(gmail_service,"gerbault.guilhem@gmail.com", "subject", "body",'')


