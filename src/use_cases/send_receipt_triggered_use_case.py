import json
from src.services.google_doc_and_drive_service import *
from src.services.gmail_service import *
from src.services.notion_service import *
from src.use_cases.send_one_receipt_use_case import *


def send_receipt_to_tenant(event, context):
    # Authentifie et crée les services nécessaires
    drive_service, _, gmail_service = authenticate_and_create_services()
    all_data = {}

    # Récupérer les données de Notion
    retrieve_notion_datas(all_data)

    # Vérifier si l'événement contient un corps
    if not event or 'body' not in event:
        print("[ERROR] Aucune donnée dans le corps de l'événement.")
        return
    
    # Essayer de décoder le JSON
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erreur lors du décodage du JSON: {e}")

        return    
    
    database_item_id = body.get('DataBaseItemID')
    # Si l'ID de la base de données est manquant
    if not database_item_id:
        print("[ERROR] DataBaseItemID non fourni dans le corps de l'événement.")
        return

    # Cherche le locataire par ID
    tenant = next((loc for loc in all_data['locataire']['results'] if loc['id'] == database_item_id), None)

    # Si le locataire n'existe pas
    if not tenant:
        print(f"[ERROR] Locataire avec l'ID {database_item_id} non trouvé.")
        return
    
    # Vérifier si on doit envoyer la quittance
    is_to_send_receipt = tenant['properties'].get('EnvoyerQuittance', {}).get('checkbox', False)
    
    if not is_to_send_receipt:
        print(f"[INFO] EnvoyerQuittance n'est pas activé pour le locataire avec l'ID {database_item_id}.")
        return

    # Envoyer la quittance pour ce locataire
    send_receipt_from_drive(tenant, drive_service, gmail_service,)