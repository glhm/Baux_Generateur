from datetime import datetime
from src.conf.info_apis import *
from src.services.google_doc_and_drive_service import *
from src.services.gmail_service import *
from src.services.notion_service import *

def send_receipt_from_drive(locataire, drive_service, gmail_service,formatted_name):
    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    print(f"[INFO] Send receipt required for {locataire_name}")

    property_envoi_quittance_result = locataire['properties'].get('EnvoiQuittanceResult', {})
    if property_envoi_quittance_result.get('select').get('name') == 'Reinit' :
        envoi_quittance_result_id = property_envoi_quittance_result.get('id')

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
            return_mail = send_email_with_attachment(
                to_address=mail_locataire,
                subject=f'Quittance de loyer {current_month_num} {current_year} {locataire_name}',
                body='Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault',
                attachment_stream=file_stream,
                attachment_name=nom_fichier,
                gmail_service=gmail_service
            )
            if return_mail:
                print("Update champ EnvoiQuittanceResult à Success")
                update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceSuccess"])
            else:
                print("Update champ EnvoiQuittanceResult à Failure")
                update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])  
        else:
            error_message = f"Le fichier {nom_fichier} n'a pas été trouvé dans Google Drive."
            print(error_message)
            perso_address = os.getenv('MAIL_PERSO')
            if perso_address is None:
                raise ValueError("La variable d'environnement 'MAIL_PERSO' n'est pas définie.")
            send_email_with_attachment(
                to_address=perso_address,
                subject=f"[ERREUR] Quittance de loyer {current_month_num} {current_year} {locataire_name}",
                body=f"Détails de l'erreur : {error_message}",
                attachment_stream=None,  # Pas de pièce jointe
                attachment_name='',  # Nom vide
                gmail_service=gmail_service
            )
            print("Update champ EnvoiQuittanceResult à Failure")
            update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])

#TODO nested if + raise ne fait rien + on envoie le mail si quand meme probleme