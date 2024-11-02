import requests
import os
from src.conf.info_apis import DATABASE_IDS


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


def retrieve_notion_datas(all_data):
    for name, database_id in DATABASE_IDS.items():
        print(f"[INFO] Fetching data for {name}...")
        data = fetch_data_from_notion(database_id)
        all_data[name] = data
        print(f"[INFO] Data fetched for {name}")

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



