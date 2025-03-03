from src.services.google_doc_and_drive_service import *
from src.services.notion_service import *
from src.use_cases.check_cases import *
from src.use_cases.generate_lease_use_case import *
from src.use_cases.send_one_receipt_use_case import *
from src.use_cases.generate_all_tenants_receipts_use_case import *

from src.adapters.notion_adapter import *

def do_tasks_required_from_user():
    drive_service, _, gmail_service = authenticate_and_create_services()
    
    all_data = {}
    retrieve_notion_datas(all_data)
    # Parcours des locataires et vérification des tâches à effectuer
    for locataire in all_data['locataire']['results']:
        # Vérification des cases cochées dans Notion
        formatted_name = build_formatted_name(locataire) 

    if is_quittance_sending_enabled(locataire):
            send_receipt_from_drive(locataire, drive_service, gmail_service,formatted_name)

