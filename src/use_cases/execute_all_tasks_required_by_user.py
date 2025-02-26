from src.services.google_doc_and_drive_service import *
from src.services.notion_service import *
from src.use_cases.check_cases import *
from src.use_cases.generate_lease_use_case import *
from src.use_cases.send_one_receipt_use_case import *
from src.use_cases.generate_all_tenants_receipts_use_case import *

from src.adapters.notion_adapter import *

def do_tasks_required_from_user():
    drive_service, docs_service, gmail_service = authenticate_and_create_services()
    
    all_data = {}
    retrieve_notion_datas(all_data)
    # Parcours des locataires et vérification des tâches à effectuer
    for locataire in all_data['locataire']['results']:
        # Vérification des cases cochées dans Notion
        formatted_name = build_formatted_name(locataire) #TODO tjrs calcule meme si pas utilise

        if is_lease_generation_enabled(locataire) or is_receipts_generation_enabled(locataire):
            all_replace_requests,type_caution,prorata_data = build_requests_from_tenant_info(locataire, all_data)
            if is_lease_generation_enabled(locataire):
                generate_lease_for_tenant(type_caution, drive_service, docs_service, all_replace_requests,formatted_name)
        
            if is_receipts_generation_enabled(locataire):
                generate_receipts_for_one_tenant(locataire, docs_service, drive_service,
                    all_replace_requests, prorata_data,formatted_name)
            
        if is_quittance_sending_enabled(locataire):
                send_receipt_from_drive(locataire, drive_service, gmail_service,formatted_name)


def build_requests_from_tenant_info(locataire, all_data) :
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

    loyer_id = info_rollup.get('loyer_id')
    if loyer_id:
        for loyer in all_data['loyer']['results']:
            if loyer['id'] == loyer_id:
                loyer_dict = extract_fields_from_database(loyer)
                #print(chambre_dict)

    # tout convertir en string
    locataire_dict_str = {key: str(value) for key, value in locataire_dict.items()}
    garant_dict_str = {key: str(value) for key, value in garant_dict.items()}
    bien_dict_str = {key: str(value) for key, value in bien_dict.items()}
    chambre_dict_str  = {key: str(value) for key, value in chambre_dict.items()}
    loyer_dict_str  = {key: str(value) for key, value in loyer_dict.items()}


    # Calcul des montants proratisés
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']

    prorata_data = compute_housing_values(loyer_dict_str, jour_arrivee, mois_arrivee)


    # Préparer les demandes de remplacement
    type_caution = locataire['properties'].get('Garantie', {}).get('select', {}).get('name', '')
    mention_speciale_loyer_data = locataire['properties'].get('MENTION_SPECIALE_LOYER', {}).get('rich_text', [])
    mention_speciale_loyer = mention_speciale_loyer_data[0]['text']['content'] if mention_speciale_loyer_data else ''   
    date_contrat = f"{jour_arrivee} {mois_arrivee} {locataire['properties']['ANNEES']['multi_select'][0]['name']}"

    type_bail = locataire['properties'].get('TypeDeBail', {}).get('select', {}).get('name', '')

    all_replace_requests = build_lease_requests(
        locataire_dict_str,
        garant_dict_str,
        bien_dict_str,
        chambre_dict_str,
        loyer_dict_str,
        prorata_data,
        type_caution,
        mention_speciale_loyer,
        date_contrat,
        type_bail
    )

    return all_replace_requests, type_caution, prorata_data


