from src.services.google_doc_and_drive_service import *
from src.adapters.notion_adapter import *
from src.domain.housing_strings import *
from src.conf.info_apis import *
from src.utils.months import *
from src.utils.receipt_naming import *

from src.adapters.notion_adapter import *
from src.adapters.build_gdoc_replace_requests import *

def generate_receipts_for_one_tenant(locataire, docs_service, drive_service, all_replace_requests, prorata_data, formatted_name):
    annee_selectionnees = locataire['properties']['ANNEES']['multi_select']

    # Obtenez le mois d'arrivée et le jour d'arrivée du locataire
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']
    annee_arrivee = locataire['properties']['{ANNEE_ARRIVEE}']['number'] 
    mois_index_arrivee = mois_list.index(mois_arrivee) + 1  # Index du mois d'arrivée dans la liste

    for annee in annee_selectionnees:
        annee_courante = annee['name']
        annees_requests = add_one_request("{{ANNEE_COURANTE}}", annee_courante)

        for mois, dernier_jour in map_jour.items():
            mois_index = mois_list.index(mois) + 1  # Index du mois en cours
            
            # Vérifiez si le mois actuel est égal ou postérieur au mois d'arrivée
            if int(annee_courante) > annee_arrivee or mois_index >= mois_index_arrivee:

                # Pour le premier mois d'arrivée, on génère la quittance avec prorata
                if mois == mois_arrivee :
                    new_quittance_doc_name = generate_quittance_doc_name(annee_courante, mois_index, formatted_name,str(prorata_data["prorata_loyer"]),str(prorata_data["prorata_charges"]))

                    print("Génération de la quittance pour le 1er mois de loyer (prorata)")
                    quittance_requests = build_receipts_requests(
                        prorata_data["prorata_total_CC"],
                        jour_arrivee,
                        titre_detail_du_reglement_quittance, 
                        paragraphe_detail_du_reglement_quittance
                    )
                else:
                    # Requêtes pour les mois normaux après le mois d'arrivée
                    quittance_requests = build_receipts_requests(prorata_data["loyer_CC"], 1, "", "")
                    new_quittance_doc_name = generate_quittance_doc_name(annee_courante, mois_index, formatted_name,str(prorata_data["loyer"]),str(prorata_data["charges"]))

                # Création et exportation du document
                all_replace_requests_month = add_one_request("{{MOIS_COURANT}}", mois) + add_one_request("{{DERNIER_JOUR}}", str(dernier_jour))

                create_and_export_doc_from_template(
                    template_id=TEMPLATE_QUITTANCE_ID,
                    new_document_name=new_quittance_doc_name,
                    replace_requests=quittance_requests + all_replace_requests + annees_requests + all_replace_requests_month,
                    folder_id=ID_REPO_QUITTANCES,
                    drive_service=drive_service,
                    docs_service=docs_service
                )
