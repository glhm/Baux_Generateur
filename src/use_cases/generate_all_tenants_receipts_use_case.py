from src.services.google_doc_and_drive_service import *
from src.adapters.extract_dicts_from_data import *
from src.domain.housing_strings import *
from src.conf.info_apis import *
from src.utils.date_utils import *
from src.utils.naming import *
from src.utils.date_utils import *

from src.adapters.extract_dicts_from_data import *
from src.adapters.build_gdoc_replace_requests import *

def generate_receipts_for_one_tenant(locataire, docs_service, drive_service, all_replace_requests, prorata_data, formatted_name,prorata_departure):
    print(f"[INFO] Traitement des quittances pour le locataire : {formatted_name}")

    annee_selectionnees = locataire['properties']['ANNEES']['multi_select']
    
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']
    annee_arrivee = locataire['properties']['{ANNEE_ARRIVEE}']['number']
    mois_index_arrivee = mois_list.index(mois_arrivee) + 1

    # Vérifier la présence des dates de départ
    jour_depart = locataire['properties'].get('{JOUR_DEPART}', {}).get('number')
    mois_depart = locataire['properties'].get('{MOIS_DEPART}', {}).get('number')
    annee_depart = locataire['properties'].get('{ANNEE_DEPART}', {}).get('number')
    id_bien = locataire['properties']['🏠 Biens']['relation'][0]['id']

    has_departure_date =prorata_departure is not None

    if has_departure_date:
        print(f"Date départ connue")

    
    for annee_obj in annee_selectionnees:
        annee_courante = int(annee_obj['name'])
        print(f"[INFO] Annee : {annee_courante}")
        
        at_folder_id = get_or_create_subfolder(
            drive_service,
            get_or_create_subfolder(
                drive_service,
                get_or_create_year_folder(drive_service, MAP_PAGE_NOTION_BIEN_TO_REPO[id_bien], annee_courante),
                "Recettes"
            ),
            "AT"
        )
        
        if not at_folder_id:
            print(f"[ERROR] Impossible de trouver ou créer le dossier AT pour l'année {annee_courante}")
            continue
        
        for mois, dernier_jour_mois in map_mois_to_dernier_jour.items():
            mois_index = mois_list.index(mois) + 1
            if int(annee_courante) < annee_arrivee or (int(annee_courante) == annee_arrivee and mois_index < mois_index_arrivee):
                continue
            if has_departure_date and compare_dates(int(annee_courante), mois_index, 1, annee_depart, mois_depart, jour_depart) > 0:
                print(f"Mois {mois} {annee_courante} après la date de départ, quittance non générée, suppression de l'ancienne si existantes")

                # Supprimer les fichiers correspondants avant de passer à la génération de la quittance
                pattern = get_quittance_pattern(mois_index, annee_courante, formatted_name)
                delete_files_matching_regex(drive_service, at_folder_id, pattern)
                
                continue  # On passe au mois suivant sans générer de quittance
            
            if has_departure_date and int(annee_courante) == annee_depart and mois_index == mois_depart:
                somme_due = prorata_departure["prorata_total_CC_depart"]  # Dernier mois
                jour_debut = 1
                titre_detail_reglement = titre_detail_du_reglement_quittance 
                paragraphe_detail_reglement = paragraphe_detail_du_reglement_quittance_dernier_mois
                montant1 = prorata_departure["prorata_loyer_depart"]
                montant2 = prorata_departure["prorata_charges_depart"]
                quittance_requests = build_receipts_requests_dernier_mois(somme_due, jour_debut, titre_detail_reglement, paragraphe_detail_reglement, annee_courante, mois, dernier_jour_mois,jour_depart,prorata_departure)


            elif int(annee_courante) == annee_arrivee and mois_index == mois_index_arrivee:
                somme_due = prorata_data["prorata_total_CC"]  # Premier mois
                jour_debut = jour_arrivee
                titre_detail_reglement = titre_detail_du_reglement_quittance 
                paragraphe_detail_reglement = paragraphe_detail_du_reglement_quittance_premier_mois
                montant1 = prorata_data["prorata_loyer"]
                montant2 = prorata_data["prorata_charges"]  
                quittance_requests = build_receipts_requests(somme_due, jour_debut, titre_detail_reglement, paragraphe_detail_reglement, annee_courante, mois, dernier_jour_mois)
           

            else:
                somme_due = prorata_data["loyer_CC"]  # Mois intermédiaires    
                jour_debut = 1
                titre_detail_reglement = "" 
                paragraphe_detail_reglement = ""
                montant1 = prorata_data["loyer"]
                montant2 = prorata_data["charges"]          
                quittance_requests = build_receipts_requests(somme_due, jour_debut, titre_detail_reglement, paragraphe_detail_reglement, annee_courante, mois, dernier_jour_mois)
            
            receipt_name = generate_quittance_doc_name(jour_creation_quittance, mois_index, annee_courante, formatted_name, montant1, montant2)
            quittance_requests_array = quittance_requests or []

            create_and_export_doc_from_template(
                template_id=TEMPLATE_QUITTANCE_ID,
                new_document_name=receipt_name,
                replace_requests=quittance_requests_array + all_replace_requests,
                folder_id=at_folder_id,
                drive_service=drive_service,
                docs_service=docs_service
            )