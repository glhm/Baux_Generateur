import os
import requests
from typing import List, Dict, Any

from src.domain.ports.tenant_repository import TenantRepository
from src.domain.entities.tenant import Tenant
from src.conf.info_apis import DATABASE_IDS

from src.adapters.mappers.guarantor_mapper import map_guarantors
from src.adapters.mappers.property_mapper import map_properties
from src.adapters.mappers.room_mapper import map_rooms
from src.adapters.mappers.rent_mapper import map_rents
from src.adapters.mappers.tenant_mapper import build_tenant


class NotionAdapter(TenantRepository):

    def __init__(self):
        self.notion_api_secret = os.getenv('NOTION_API_SECRET')
        if not self.notion_api_secret:
            raise ValueError("NOTION_API_SECRET environment variable is not defined.")
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_secret}",
            "Notion-Version": "2022-06-28",
        }

    def get_all_concerned_tenants(self) -> List[Tenant]:
        """
        Fetches tenants from Notion where at least one of the action checkboxes
        (EnvoyerQuittance, ActiverGeneration, ActiverGenerationQuittances) is checked,
        then constructs full Tenant entities with related data.
        """
        # 1. Fetch locataires with checkbox filter
        locataires_raw = self._fetch_concerned_locataires()

        # 2. Fetch related databases (no filter needed)
        raw_data = self._fetch_related_databases()

        # 3. Map related data
        guarantors_map = map_guarantors(raw_data.get('garants', {}))
        properties_map = map_properties(raw_data.get('bien', {}))
        rooms_map = map_rooms(raw_data.get('chambres', {}))
        rents_map = map_rents(raw_data.get('loyer', {}))

        # 4. Build Tenant entities
        tenants: List[Tenant] = []
        for loc_data in locataires_raw:
            tenant = build_tenant(loc_data, guarantors_map, properties_map, rooms_map, rents_map)
            if tenant:
                tenants.append(tenant)

        return tenants

    def _fetch_concerned_locataires(self) -> List[Dict[str, Any]]:
        """
        Query the locataire database with an OR filter on the three action checkboxes.
        Returns only tenants that have at least one checkbox checked.
        """
        db_id = DATABASE_IDS['locataire']
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

        response = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=self.headers,
            json=body
        )
        response.raise_for_status()
        return response.json().get('results', [])

    def _fetch_related_databases(self) -> Dict[str, Any]:
        """Fetch all related databases (garants, bien, chambres, loyer) without filters."""
        all_data = {}
        related_dbs = {k: v for k, v in DATABASE_IDS.items() if k != 'locataire'}
        for name, db_id in related_dbs.items():
            response = requests.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=self.headers
            )
            response.raise_for_status()
            all_data[name] = response.json()
        return all_data
