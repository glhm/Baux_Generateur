from datetime import datetime
from src.conf.info_apis import *
from src.services.google_doc_and_drive_service import *
from src.services.gmail_service import *
from src.services.notion_service import *
from src.utils.naming import *
import os

def send_error_email(subject, body, gmail_service):
    perso_address = os.getenv('MAIL_PERSO')
    if not perso_address:
        raise ValueError("❌ La variable d'environnement 'MAIL_PERSO' n'est pas définie.")
    
    print(f"📧 Envoi d'un mail d'erreur à {perso_address}")
    send_email_with_attachment(
        to_address=perso_address,
        subject=subject,
        body=body,
        attachment_stream=None,  # Pas de pièce jointe
        attachment_name='',  # Nom vide
        gmail_service=gmail_service
    )

def send_receipt_from_drive(locataire, drive_service, gmail_service, formatted_name):
    locataire_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content']
    print(f"[INFO] Envoi quittance requis pour {locataire_name}")

    property_envoi_quittance_result = locataire['properties'].get('EnvoiQuittanceResult', {})
    if property_envoi_quittance_result.get('select', {}).get('name') != 'Reinit':
        return  # Pas besoin d'envoyer la quittance si le statut n'est pas "Reinit"

    envoi_quittance_result_id = property_envoi_quittance_result.get('id')
    current_date = datetime.now()
    current_year = current_date.strftime('%Y')
    current_month_num = current_date.strftime('%m')
    mail_locataire = locataire['properties']['Mail']['rich_text'][0]['text']['content']
    id_bien = locataire['properties']['🏠 Biens']['relation'][0]['id']
  # 📌 Motif regex pour xx entre 00 et 30
    pattern = get_quittance_pattern(current_month_num,current_year,formatted_name)

    #id repo
    current_year_folder = get_or_create_year_folder(drive_service, MAP_PAGE_NOTION_BIEN_TO_REPO[id_bien], current_year)
    recettes_folder = get_or_create_subfolder(drive_service, current_year_folder, "Recettes")
    at_folder = get_or_create_subfolder(drive_service, recettes_folder, f"AT")

    if not at_folder:
        error_message = f"🚫 Erreur : Impossible de trouver ou créer le dossier AT pour l'année {current_year}."
        print(error_message)
        send_error_email(
            subject=f"[ERREUR] Dossier AT manquant pour {locataire_name}",
            body=f"Détails de l'erreur : {error_message}",
            gmail_service=gmail_service
        )
        update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
        return

    query = f"name contains 'Quittance--' and '{at_folder}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])


    # 📌 Filtrer les fichiers selon le modèle flexible et précis
    matching_files = [f for f in files if pattern.match(f['name'])]

    # ❌ Gestion des cas d'erreur avec la fonction centralisée
    if len(matching_files) == 0:
        error_message = f"🚫 Aucun fichier correspondant trouvé pour {formatted_name} en {current_month_num}/{current_year}."
        print(error_message)
        send_error_email(
            subject=f"[ERREUR] Quittance manquante pour {locataire_name}",
            body=f"Détails de l'erreur : {error_message}",
            gmail_service=gmail_service
        )
        update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
        return

    if len(matching_files) > 1:
        error_message = f"🚫 Erreur : Plusieurs fichiers trouvés pour {formatted_name} en {current_month_num}/{current_year}."
        print(error_message)
        send_error_email(
            subject=f"[ERREUR] Multiples quittances pour {locataire_name}",
            body=f"Détails de l'erreur : {error_message}",
            gmail_service=gmail_service
        )
        update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
        return

    # ✅ Un seul fichier trouvé, on continue
    file_id = matching_files[0]['id']
    file_name = matching_files[0]['name']
    file_stream = download_file_from_drive(file_id, drive_service)
    print(f"✅ Fichier correspondant trouvé : {file_name}")

    # ✉️ Envoyer l'email avec la pièce jointe
    return_mail = send_email_with_attachment(
        to_address=mail_locataire,
        subject=f'Quittance de loyer {current_month_num} {current_year} {locataire_name}',
        body='Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault',
        attachment_stream=file_stream,
        attachment_name=file_name,
        gmail_service=gmail_service
    )

    # 📌 Mise à jour de l'état dans Notion
    if return_mail:
        print("📌 Mise à jour du champ EnvoiQuittanceResult à Success")
        update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceSuccess"])
    else:
        print("📌 Mise à jour du champ EnvoiQuittanceResult à Failure")
        update_notion_property(locataire['id'], envoi_quittance_result_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
