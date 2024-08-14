from googleapiclient.discovery import build
from notion_database import *
from google_doc_and_drive import *
from datetime import datetime
from googlemail import *
from mystrings import *
import locale
import os
from maths_baux import *
from replace_requests import *
from info_apis import *



drive_service, docs_service, gmail_service = authenticate_and_create_services()


# 2. Modifiez le nouveau document
all_data = {}
retrieve_notion_datas(all_data)

for locataire in all_data['locataire']['results']:
    # Vérification de la case ActiverGeneration
    activer_generation_baux = locataire['properties'].get('ActiverGeneration', {}).get('checkbox', False)
    activer_generation_quittance = locataire['properties'].get('ActiverGenerationQuittances', {}).get('checkbox', False)
    envoyer_quittance = locataire['properties'].get('EnvoyerQuittance', {}).get('checkbox', False)

    if not activer_generation_baux and not activer_generation_quittance and not envoyer_quittance:
        continue  # Si la case n'est pas cochée, on passe au locataire suivant

    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    formatted_name = locataire_name.replace(" ", "_").replace("'", "_").replace(",", "")

    locataire_dict,info_rollup = extract_fields_from_locataire_database(locataire)

    garant_dict = {}
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
    garant_dict_str = {key: str(value) for key, value in garant_dict.items()}
    bien_dict_str = {key: str(value) for key, value in bien_dict.items()}
    chambre_dict_str  = {key: str(value) for key, value in chambre_dict.items()}


    # Calcul des montants proratisés
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']
    
    prorata_data = calculate_prorata_for_first_month(chambre_dict, jour_arrivee, mois_arrivee)


    # Préparer les demandes de remplacement
    type_caution = locataire['properties'].get('Garantie', {}).get('select', {}).get('name', '')
    mention_speciale_loyer_data = locataire['properties'].get('MENTION_SPECIALE_LOYER', {}).get('rich_text', [])
    mention_speciale_loyer = mention_speciale_loyer_data[0]['text']['content'] if mention_speciale_loyer_data else ''   
    date_contrat = f"{jour_arrivee} {mois_arrivee} {locataire['properties']['ANNEES']['multi_select'][0]['name']}"

    type_bail = locataire['properties'].get('TypeDeBail', {}).get('select', {}).get('name', '')

    all_replace_requests = prepare_replace_requests(
        locataire_dict_str,
        garant_dict_str,
        bien_dict_str,
        chambre_dict_str,
        prorata_data,
        type_caution,
        mention_speciale_loyer,
        date_contrat,
        type_bail
    )
    if activer_generation_baux :
        new_document_name = f"bail_location_{formatted_name}"

        process_document(
        template_id=ID_TEMPLATE_BAIL_MEUBLE,
        new_document_name=new_document_name,
        replace_requests=all_replace_requests,
        folder_id=ID_REPO_BAUX,
        drive_service=drive_service,
        docs_service=docs_service
        )

        if type_caution == "Physique" :
            new_caution_doc_name = f"Acte_de_caution_solidaire_{formatted_name}"
            process_document(
                template_id=CAUTION_ID,
                new_document_name=new_caution_doc_name,
                replace_requests=all_replace_requests,
                folder_id=ID_REPO_BAUX,
                drive_service=drive_service,
                docs_service=docs_service
            )

    if activer_generation_quittance :
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
                        quittance_requests = []
                        quittance_requests.extend(add_one_request("{{SOMME_DUE}}", "{:.2f}".format(prorata_data["prorata_total_CC"])))
                        quittance_requests.extend(add_one_request("{{JOUR_DEBUT_QUITTANCE}}", str(jour_arrivee)))
                        quittance_requests.extend(add_one_request("{{TITRE_DETAIL_DU_REGLEMENT}}", titre_detail_du_reglement_quittance))
                        quittance_requests.extend(add_one_request("{{PARAGRAPHE_DETAIL_REGLEMENT_QUITTANCES}}", paragraphe_detail_du_reglement_quittance))

                        process_document(
                            template_id=TEMPLATE_QUITTANCE_ID,
                            new_document_name=new_quittance_doc_name,
                            replace_requests=quittance_requests+all_replace_requests + annees_requests+ all_replace_requests_month,
                            folder_id=ID_REPO_QUITTANCES,
                            drive_service=drive_service,
                            docs_service=docs_service
                        )

                        # Marquer le début de la génération des quittances normales
                        start_generation_quittances = True
                else:
                    # Génération des quittances normales pour tous les mois
                    quittance_requests = []
                    quittance_requests.extend(add_one_request("{{SOMME_DUE}}", "{:.2f}".format(prorata_data["loyer_CC"])))
                    quittance_requests.extend(add_one_request("{{JOUR_DEBUT_QUITTANCE}}", "1"))
                    quittance_requests.extend(add_one_request("{{TITRE_DETAIL_DU_REGLEMENT}}", ""))
                    quittance_requests.extend(add_one_request("{{PARAGRAPHE_DETAIL_REGLEMENT_QUITTANCES}}", ""))
                    process_document(
                    template_id=TEMPLATE_QUITTANCE_ID,
                    new_document_name=new_quittance_doc_name,
                    replace_requests=quittance_requests+all_replace_requests + annees_requests + all_replace_requests_month,
                    folder_id=ID_REPO_QUITTANCES,
                    drive_service=drive_service,
                    docs_service=docs_service
                    )

    if envoyer_quittance:
        print(f"Envoi quittance locataire {locataire_name}")
        current_date = datetime.now()
        current_year = current_date.strftime('%Y')
        current_month_num = current_date.strftime('%m')  # Mois sous forme de numéro
        mail_locataire = locataire['properties']['Mail']['rich_text'][0]['text']['content']
        
        # Construire le nom du fichier de quittance attendu
        nom_fichier = f"Quittance_de_loyer_{current_year}_{current_month_num}_{formatted_name}"
        
        # Utiliser la fonction de recherche de fichier dans Google Drive
        query = f"name='{nom_fichier}' and '{ID_REPO_QUITTANCES}' in parents"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            file_stream = download_file_from_drive(file_id, drive_service)
            print(f"Fichier {nom_fichier} trouvé")

            # Envoyer l'email avec la pièce jointe téléchargée
            send_email_with_attachment(
                to_address=mail_locataire,
                subject=f'Quittance de loyer {current_month_num} {current_year} {locataire_name}',
                body='Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault',
                attachment_stream=file_stream,
                attachment_name=nom_fichier,
                gmail_service=gmail_service
            )
        else:
            error_message = f"Le fichier {nom_fichier} n'a pas été trouvé dans Google Drive."
            print(error_message)
            
            send_email_with_attachment(
                to_address="gerbault.guilhem@gmail.com",
                subject=f"[ERREUR] Quittance de loyer {current_month_num} {current_year} {locataire_name}",
                body=f"Détails de l'erreur : {error_message}",
                attachment_stream=None,  # Pas de pièce jointe
                attachment_name='',  # Nom vide
                gmail_service=gmail_service
            )
