from src.domain.compute_housing_values import *

def extract_fields(properties):
    """
    Extrait les valeurs des champs des propriétés de la base de données Notion.

    :param properties: Dictionnaire contenant les propriétés de l'élément Notion.
    :return: Dictionnaire avec les champs extraits.
    """
    field_values_dict = {}
    for field_name, field_data in properties.items():
        if 'text' in field_data and field_data['text']:
            field_values_dict[field_name] = field_data['text'][0]['text']['content']
        elif 'rich_text' in field_data and field_data['rich_text']:
            field_values_dict[field_name] = field_data['rich_text'][0]['text']['content']
        elif 'title' in field_data and field_data['title']:
            field_values_dict[field_name] = field_data['title'][0]['text']['content']
        elif 'number' in field_data and field_data['number']:
            field_values_dict[field_name] = field_data['number']
    
    return field_values_dict

def extract_fields_from_locataire_database(locataire_database):
    """
    Extrait les valeurs des champs spécifiques à la base de données des locataires
    et les relations vers d'autres données.
    """
    tenant_values_dict = extract_fields(locataire_database['properties'])
    info_rollup = {}
    # emotes because Notion 
    if '🪙 Garants' in locataire_database['properties'] and locataire_database['properties']['🪙 Garants']['relation']:
        guarantor_id = locataire_database['properties']['🪙 Garants']['relation'][0]['id']
        info_rollup['guarantor_id'] = guarantor_id
    if '🏠 Biens' in locataire_database['properties'] and locataire_database['properties']['🏠 Biens']['relation']:
        bien_id = locataire_database['properties']['🏠 Biens']['relation'][0]['id']
        info_rollup['bien_id'] = bien_id
    if '🛏️ Chambres' in locataire_database['properties'] and locataire_database['properties']['🛏️ Chambres']['relation']:
        chambre_id = locataire_database['properties']['🛏️ Chambres']['relation'][0]['id']
        info_rollup['chambre_id'] = chambre_id
    if '💲 Loyers' in locataire_database['properties'] and locataire_database['properties']['💲 Loyers']['relation']:
        loyer_id = locataire_database['properties']['💲 Loyers']['relation'][0]['id']
        info_rollup['loyer_id'] = loyer_id

    return tenant_values_dict, info_rollup

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


def extract_fields_from_database(notion_database_data):
    """
    Extrait les valeurs des champs d'une base de données Notion spécifique.
    """
    return extract_fields(notion_database_data['properties'])

def build_formatted_name(locataire):
    formatted_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content'].replace(" ", "_").replace("'", "_").replace(",", "")
    return formatted_name

def calculate_prorata(locataire, chambre_dict):
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']
    return compute_housing_values(chambre_dict, jour_arrivee, mois_arrivee)

