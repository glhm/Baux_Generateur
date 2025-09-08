from src.services.google_doc_and_drive_service import *
from src.services.notion_service import *
from src.use_cases.check_cases import *
from src.use_cases.generate_lease_use_case import *
from src.use_cases.send_one_receipt_use_case import *
from src.use_cases.generate_all_tenants_receipts_use_case import *
from src.adapters.extract_dicts_from_data import *

def do_tasks_required_from_user():
    drive_service, docs_service, gmail_service = authenticate_and_create_services()
    
    all_data = {}
    retrieve_notion_datas(all_data)
    # Parcours des locataires et vérification des tâches à effectuer
    for locataire in all_data['locataire']['results']:
        # Vérification des cases cochées dans Notion
        formatted_name = build_formatted_name(locataire) #TODO tjrs calcule meme si pas utilise

        if is_lease_generation_enabled(locataire) or is_receipts_generation_enabled(locataire):
            all_replace_requests,type_caution,prorata_data,prorata_departure = build_requests_from_tenant_info(locataire, all_data)
            if is_lease_generation_enabled(locataire):
                generate_lease_for_tenant(type_caution, drive_service, docs_service, all_replace_requests,formatted_name)
        
            if is_receipts_generation_enabled(locataire):
                generate_rental_deposit_receipt_for_one_tenant(formatted_name,docs_service,drive_service, all_replace_requests)
               # generate_receipts_for_one_tenant(locataire, docs_service, drive_service, all_replace_requests, prorata_data,formatted_name,prorata_departure)
        if is_quittance_sending_enabled(locataire):
                send_receipt_from_drive(locataire, drive_service, gmail_service,formatted_name)

