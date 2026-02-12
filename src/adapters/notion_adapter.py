import os

import requests

from typing import List, Dict, Any


from src.ports.tenant_repository import LeaseRepository

from src.domain.entities.lease import Lease

from src.conf.info_apis import DATABASE_IDS


from src.adapters.mappers.guarantor_mapper import map_guarantors

from src.adapters.mappers.property_mapper import map_properties
from src.adapters.mappers.room_mapper import map_rooms
from src.adapters.mappers.rent_mapper import map_rents

from src.adapters.mappers.lease_mapper import build_lease


# Need to check if I need to update this file to fix usage of map_rents

# map_rents returns Dict[str, Financials] now (was Numbers)

# NotionAdapter just passes rents_map to build_lease.

# build_lease expects Dict[str, Financials].

# So direct pass-through is fine, but I should ensure type hinting import is updated if I used it.

# NotionAdapter step 277 didn't import Numbers/Financials explicitly for type hint of map variable, 

# it just assigned `rents_map = map_rents(...)`.

# But `build_lease` signature in `lease_mapper.py` mentions `Financials`.


# Re-writing NotionAdapter to just ensure imports are clean and correct context.

# No logic change needed except maybe imports.


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

        raw_data = self._fetch_related_databases()


        guarantors_map = map_guarantors(raw_data.get('garants', {}))

        properties_map = map_properties(raw_data.get('bien', {}))

        rooms_map = map_rooms(raw_data.get('chambres', {}))

        rents_map = map_rents(raw_data.get('loyer', {}))


        leases: List[Lease] = []

        for loc_data in locataires_raw:

            lease = build_lease(loc_data, guarantors_map, properties_map, rooms_map, rents_map)

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


    def _fetch_related_databases(self) -> Dict[str, Any]:

        all_data = {}

        related_dbs = {k: v for k, v in DATABASE_IDS.items() if k != 'locataire'}

        for name, db_id in related_dbs.items():

            response = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query", headers=self.headers)

            response.raise_for_status()

            all_data[name] = response.json()
        return all_data

