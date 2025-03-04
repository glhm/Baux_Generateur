# replace_strings_in_doc.py

from src.domain.housing_strings import *
from src.adapters.extract_dicts_from_data import *

def build_lease_requests(locataire_dict_str, guarant_dict_str, bien_dict_str, chambre_dict_str,loyer_dict_str, prorata_data, type_caution, mention_speciale_loyer, date_contrat, type_bail):
    """
    Prépare les demandes de remplacement pour le modèle de document avec les informations fournies.

    :param locataire_dict_str: Dictionnaire avec les informations du locataire sous forme de chaîne.
    :param guarant_dict_str: Dictionnaire avec les informations du garant sous forme de chaîne.
    :param bien_dict_str: Dictionnaire avec les informations du bien sous forme de chaîne.
    :param chambre_dict_str: Dictionnaire avec les informations de la chambre sous forme de chaîne.
    :param loyer_dict_str: Dictionnaire avec les informations des montants des loyers
    :param prorata_data: Dictionnaire avec les données proratisées calculées.
    :param type_caution: Type de caution.
    :param mention_speciale_loyer: Mention spéciale du loyer.
    :param date_contrat: Date du contrat.
    :param type_bail: Type de bail.
    :return: Liste des demandes de remplacement.
    """
    all_replace_requests = []

    # Gestion des types de caution
    if type_caution == "Visale":
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_visale))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", ""))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", ""))
        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", doc_visale))
    else:
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_physique))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", la_caution_physique))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", signature_des_garants))
        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", ""))

    # Ajout des informations provenant des dictionnaires
    all_replace_requests.extend(build_replace_requests_from_dict(locataire_dict_str))
    all_replace_requests.extend(build_replace_requests_from_dict(guarant_dict_str))
    all_replace_requests.extend(build_replace_requests_from_dict(bien_dict_str))
    all_replace_requests.extend(build_replace_requests_from_dict(chambre_dict_str))
    all_replace_requests.extend(build_replace_requests_from_dict(loyer_dict_str))

    # Ajout des informations calculées
    all_replace_requests.extend(add_one_request("{{TOTAL_1ER_MOIS}}", str(prorata_data["total_premier_mois"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_TOTAL_CC}}", str(prorata_data["prorata_total_CC"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_LOYER}}", str(prorata_data["prorata_loyer"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_CHARGES}}", str(prorata_data["prorata_charges"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_LOYER}}", str(prorata_data["loyer"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_CHARGES}}", str(prorata_data["charges"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_GARANTIES}}", str(prorata_data["montant_garanties"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_TOTAL}}", str(prorata_data["loyer_CC"])))
    
    all_replace_requests.extend(add_one_request("{{NOMBRE_JOURS_PREMIER_MOIS}}", str(prorata_data["nombre_de_jours_premier_mois"])))

    if mention_speciale_loyer:
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", mention_speciale_loyer))
    else:
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", ""))

    all_replace_requests.extend(add_one_request("{{DATE_CONTRAT}}", date_contrat))

    # Gestion du type de bail
    if type_bail == 'Etudiant':
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_etudiant_duree))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", bail_etudiant_titre))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_etudiant))
        all_replace_requests.extend(add_one_request("{{MENTION_RECONDUCTION_MEUBLE}}", ""))

    else:
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_meuble_duree))
        all_replace_requests.extend(add_one_request("{{MENTION_RECONDUCTION_MEUBLE}}", reconduction_meuble))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_meuble))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", str("")))

    return all_replace_requests


def build_receipts_requests(somme_due, jour_debut_quittance, titre_detail_reglement, paragraphe_detail_reglement,annee_courante,mois_courant,nombre_jour_mois):
    quittance_requests = []

    # Ajout des informations spécifiques à la quittance
    quittance_requests.extend(add_one_request("{{SOMME_DUE}}", str(somme_due)))
    quittance_requests.extend(add_one_request("{{JOUR_DEBUT_QUITTANCE}}", str(jour_debut_quittance)))
    quittance_requests.extend(add_one_request("{{TITRE_DETAIL_DU_REGLEMENT}}", titre_detail_reglement))
    quittance_requests.extend(add_one_request("{{PARAGRAPHE_DETAIL_REGLEMENT_QUITTANCES}}", paragraphe_detail_reglement))
    quittance_requests.extend(add_one_request("{{ANNEE_COURANTE}}", str(annee_courante)))
    quittance_requests.extend(add_one_request("{{MOIS_COURANT}}", mois_courant))
    quittance_requests.extend(add_one_request("{{NOMBRE_JOUR_MOIS}}", str(nombre_jour_mois)))


    return quittance_requests

def build_receipts_requests_dernier_mois(somme_due, jour_debut_quittance, titre_detail_reglement, paragraphe_detail_reglement,annee_courante,mois_courant,nombre_jour_mois,jour_depart,prorata_data_depart):
    quittance_requests = build_receipts_requests(somme_due, jour_debut_quittance, titre_detail_reglement, paragraphe_detail_reglement,annee_courante,mois_courant,nombre_jour_mois)
    quittance_requests.extend(add_one_request("{{JOUR_DEPART}}", str(jour_depart)))      
    quittance_requests.extend(add_one_request("{{PRORATA_TOTAL_CC_DEPART}}", str(prorata_data_depart["prorata_total_CC_depart"])))
    quittance_requests.extend(add_one_request("{{PRORATA_LOYER_DEPART}}", str(prorata_data_depart["prorata_loyer_depart"])))
    quittance_requests.extend(add_one_request("{{PRORATA_CHARGES_DEPART}}", str(prorata_data_depart["prorata_charges_depart"])))
    return quittance_requests


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
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number'] #TODO passer en chiffre 

    prorata_data = compute_housing_values(loyer_dict_str, jour_arrivee, mois_arrivee)
    
    jour_depart = locataire.get('properties', {}).get('{JOUR_DEPART}', {}).get('number')
    mois_depart = locataire.get('properties', {}).get('{MOIS_DEPART}', {}).get('number')
    annee_depart = locataire.get('properties', {}).get('{ANNEE_DEPART}', {}).get('number')
    
    prorata_departure = None  
    if jour_depart is not None and mois_depart is not None and annee_depart is not None:
        prorata_departure = compute_departure_values(loyer_dict_str,jour_depart,mois_depart)

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

    return all_replace_requests, type_caution, prorata_data,prorata_departure

def build_replace_requests_from_dict(data_dict):
    requests = []
    for field, value in data_dict.items():
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': f"{{{field}}}",
                    'matchCase': True,
                },
                'replaceText': value,
            }
        })
    return requests

def add_one_request(field,value):
    requests = []
    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': f"{field}",
                'matchCase': True,
            },
            'replaceText': value,
        }
    })
    return requests




