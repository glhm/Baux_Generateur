import requests
import os
from info_apis import DATABASE_IDS


def fetch_data_from_notion(database_id):
    notion_api_secret = os.getenv('NOTION_API_SECRET')
    if notion_api_secret is None:
        raise ValueError("La variable d'environnement 'NOTION_API_SECRET' n'est pas définie.")
    headers = {
    "Authorization": f"Bearer {notion_api_secret}",
    "Notion-Version": "2022-06-28",  # Cette version peut évoluer, consultez la documentation Notion
    }

    response = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers)
    return response.json()


def update_notion_property(page_id, property_name, select_option_id):
    """
    Met à jour une propriété de type 'select' d'une page dans Notion.

    :param page_id: ID de la page à mettre à jour.
    :param property_name: Nom de la propriété à mettre à jour.
    :param select_option_id: ID de l'option 'select' à définir.
    """
    notion_api_secret = os.getenv('NOTION_API_SECRET')
    if notion_api_secret is None:
        raise ValueError("La variable d'environnement 'NOTION_API_SECRET' n'est pas définie.")

    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {notion_api_secret}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"  # Utilisez la version API appropriée
    }
    
    data = {
        "properties": {
            property_name: {
                "select": {
                    "id": select_option_id
                }
            }
        }
    }

    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Propriété mise à jour avec succès pour la page.")
    else:
        print(f"Erreur lors de la mise à jour de la propriété '{property_name}' pour la page {page_id}. Réponse: {response.text}")

# Exemple d'utilisation:
# page_id = '2c98e18b-dcb4-487c-8f5b-bc46bad9a462'
# select_option_id = '124546fa-5451-4b30-b1ac-5122f7740d6e'  # ID de l'option 'Success'
# update_notion_property(page_id, 'EnvoiQuittanceResult', select_option_id)

def extract_related_data(data_type, info_rollup, all_data):
    """
    Extrait les informations associées à un type de données spécifique à partir des données complètes.

    :param data_type: Type de données à extraire ('garants', 'bien', 'chambres').
    :param info_rollup: Dictionnaire contenant les ID des données associées.
    :param all_data: Dictionnaire contenant toutes les données.
    :return: Dictionnaire avec les informations extraites.
    """
    data_id = info_rollup.get(f'{data_type}')
    if not data_id:
        return {}

    # Recherche dans les données complètes
    for item in all_data[data_type]['results']:
        if item['id'] == data_id:
            return extract_fields_from_database(item)
    
    return {}

def retrieve_notion_datas(all_data):
    for name, database_id in DATABASE_IDS.items():
        print(f"[INFO] Fetching data for {name}...")
        data = fetch_data_from_notion(database_id)
        all_data[name] = data
        print(f"[INFO] Data fetched for {name}")

# Maintenant, la variable `all_data` contient les données de toutes vos bases de données.
# Par exemple, pour accéder aux données de "bien", utilisez : all_data["bien"]


def build_replace_requests(data_dict):
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
    field_values_dict = extract_fields(locataire_database['properties'])
    info_rollup = {}

    if '🪙 Garants' in locataire_database['properties'] and locataire_database['properties']['🪙 Garants']['relation']:
        guarantor_id = locataire_database['properties']['🪙 Garants']['relation'][0]['id']
        info_rollup['guarantor_id'] = guarantor_id
    if '🏠 Biens' in locataire_database['properties'] and locataire_database['properties']['🏠 Biens']['relation']:
        bien_id = locataire_database['properties']['🏠 Biens']['relation'][0]['id']
        info_rollup['bien_id'] = bien_id
    if '🛏️ Chambres' in locataire_database['properties'] and locataire_database['properties']['🛏️ Chambres']['relation']:
        chambre_id = locataire_database['properties']['🛏️ Chambres']['relation'][0]['id']
        info_rollup['chambre_id'] = chambre_id

    return field_values_dict, info_rollup

def extract_fields_from_database(notion_database_data):
    """
    Extrait les valeurs des champs d'une base de données Notion spécifique.
    """
    return extract_fields(notion_database_data['properties'])
