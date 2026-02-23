import os
import requests
from typing import List, Dict, Any, Set
from src.ports.lease_repository import LeaseRepository
from src.domain.entities.lease import Lease
from src.conf.info_apis import DATABASE_IDS
from src.adapters.mappers.lease_mapper import build_lease


class NotionAdapter(LeaseRepository):


    def __init__(self):

        self.notion_api_secret = os.getenv('NOTION_API_SECRET')

        if not self.notion_api_secret:

            raise ValueError("NOTION_API_SECRET environment variable is not defined.")

        self.headers = {

            "Authorization": f"Bearer {self.notion_api_secret}",

            "Notion-Version": "2022-06-28",

        }


    def get_all_concerned_leases(self) -> List[Lease]:
        """

        Fetches tenants to generate leases for.
        """

        locataires_raw = self._fetch_concerned_locataires()

        raw_data = self._fetch_related_databases(locataires_raw)

        leases: List[Lease] = []

        for loc_data in locataires_raw:

            lease = build_lease(
                loc_data,
                raw_data,
            )

            if lease:

                leases.append(lease)

        return leases


    def update_lease_status(self, lease_id: str, status_id: str):

        """Update the EnvoiQuittanceResult status for a lease (tenant page)."""

        body = {

            "properties": {

                "EnvoiQuittanceResult": {

                    "select": {

                        "id": status_id

                    }

                }

            }

        }

        response = requests.patch(

            f"https://api.notion.com/v1/pages/{lease_id}",

            headers=self.headers,

            json=body

        )

        response.raise_for_status()


    def _fetch_concerned_locataires(self) -> List[Dict[str, Any]]:

        db_id = DATABASE_IDS['locataire']

        # Same filter logic

        body = {

            "filter": {

                "or": [

                    {

                        "property": "EnvoyerQuittance",

                        "checkbox": {"equals": True}

                    },

                    {

                        "property": "ActiverGeneration",

                        "checkbox": {"equals": True}

                    },

                    {

                        "property": "ActiverGenerationQuittances",

                        "checkbox": {"equals": True}

                    }

                ]

            }

        }

        response = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query", headers=self.headers, json=body)

        response.raise_for_status()

        return response.json().get('results', [])


    def _fetch_related_databases(self, locataires_raw: List[Dict[str, Any]]) -> Dict[str, Any]:

        related_ids = self._extract_related_ids(locataires_raw)

        return {
            'garants': {'results': self._fetch_pages_by_ids(related_ids['garants'])},
            'bien': {'results': self._fetch_pages_by_ids(related_ids['bien'])},
            'chambres': {'results': self._fetch_pages_by_ids(related_ids['chambres'])},
            'loyer': {'results': self._fetch_pages_by_ids(related_ids['loyer'])},
        }

    def _extract_related_ids(self, locataires_raw: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        related_ids: Dict[str, Set[str]] = {
            'garants': set(),
            'bien': set(),
            'chambres': set(),
            'loyer': set(),
        }

        for locataire in locataires_raw:
            props = locataire.get('properties', {})

            if props.get('Garantie', {}).get('select', {}).get('name') != 'Visale':
                related_ids['garants'].update(
                    rel['id'] for rel in props.get('🪙 Garants', {}).get('relation', [])
                )

            related_ids['bien'].update(
                rel['id'] for rel in props.get('🏠 Biens', {}).get('relation', [])
            )
            related_ids['chambres'].update(
                rel['id'] for rel in props.get('🛏️ Chambres', {}).get('relation', [])
            )
            related_ids['loyer'].update(
                rel['id'] for rel in props.get('💲 Loyers', {}).get('relation', [])
            )

        return related_ids

    def _fetch_pages_by_ids(self, page_ids: Set[str]) -> List[Dict[str, Any]]:
        pages: List[Dict[str, Any]] = []

        for page_id in page_ids:
            response = requests.get(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            pages.append(response.json())

        return pages
