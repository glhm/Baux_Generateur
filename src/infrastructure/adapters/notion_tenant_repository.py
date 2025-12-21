import requests
import os
from typing import List, Optional
from dacite import from_dict, Config
from src.domain.ports.repositories import TenantRepository
from src.domain.entities.tenant import Tenant
from src.domain.entities.value_objects import Address
from src.application.dtos.notion_dtos import NotionTenantDTO
from src.domain.exceptions.custom_exceptions import InfrastructureException

class NotionRepository(TenantRepository):
    def __init__(self, database_id: str):
        self.database_id = database_id
        self.api_key = os.getenv('NOTION_API_SECRET')
        if not self.api_key:
             # In a real app, maybe log a warning or fail, but let's assume it's checked at startup
             pass 

    def get_all_tenants(self) -> List[Tenant]:
        if not self.api_key:
            raise InfrastructureException("Notion API Key not found")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            tenants = []
            for item in data.get('results', []):
                # Mapping logic: Notion JSON -> NotionTenantDTO
                # This part is tricky because Notion's API returns deep nested structure
                # (properties -> key -> type -> value).
                # We need a parser here.
                flat_data = self._flatten_notion_properties(item['properties'])
                flat_data['page_id'] = item['id']
                
                # Use dacite to create DTO
                dto = from_dict(data_class=NotionTenantDTO, data=flat_data, config=Config(check_types=False))
                
                # Convert DTO -> Domain Entity
                tenant = self._map_dto_to_entity(dto)
                # Attaching the flag purely for the UseCase to see it (hack for the refactor scope)
                setattr(tenant, 'generate_lease_flag', dto.generate_lease) 
                
                tenants.append(tenant)
                
            return tenants

        except Exception as e:
            raise InfrastructureException(f"Failed to fetch tenants from Notion: {e}")

    def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        # Inefficient implementation for now: fetch all and filter
        tenants = self.get_all_tenants()
        for t in tenants:
            if t.full_name == name: # Or strict check on first/last
                return t
        return None

    def _flatten_notion_properties(self, properties: dict) -> dict:
        """
        Extracts values from Notion's complex property structure into a flat dict 
        matching NotionTenantDTO fields.
        """
        flat = {}
        # Example mapping (needs to match actual Notion column names EXACTLY or be mapped)
        # Assuming Notion columns are: "Nom", "Prenom", "Email", etc.
        
        flat['nom'] = self._get_safe_value(properties.get('Nom'))
        flat['prenom'] = self._get_safe_value(properties.get('Prenom'))
        flat['email'] = self._get_safe_value(properties.get('Email'))
        flat['telephone'] = self._get_safe_value(properties.get('Telephone'))
        flat['adresse_postale'] = self._get_safe_value(properties.get('Adresse'))
        flat['ville'] = self._get_safe_value(properties.get('Ville'))
        flat['code_postal'] = self._get_safe_value(properties.get('CodePostal'))
        flat['type_bail'] = self._get_safe_value(properties.get('TypeBail'))
        flat['garant_type'] = self._get_safe_value(properties.get('GarantType')) 
        
        flat['generate_lease'] = self._get_safe_value(properties.get('GeneruerBail'), default=False)
        flat['generate_receipt'] = self._get_safe_value(properties.get('GenererQuittance'), default=False)
        flat['send_receipt'] = self._get_safe_value(properties.get('EnvoyerQuittance'), default=False)

        return flat

    def _get_safe_value(self, prop: dict, default=None):
        if not prop:
            return default
        p_type = prop.get('type')
        if p_type == 'rich_text':
             content = prop.get('rich_text', [])
             return content[0].get('text', {}).get('content') if content else default
        elif p_type == 'title':
             content = prop.get('title', [])
             return content[0].get('text', {}).get('content') if content else default
        elif p_type == 'select':
             return prop.get('select', {}).get('name') if prop.get('select') else default
        elif p_type == 'checkbox':
             return prop.get('checkbox', False)
        elif p_type == 'email':
             return prop.get('email', default)
        elif p_type == 'phone_number':
             return prop.get('phone_number', default)
        # Add other types as needed
        return default

    def _map_dto_to_entity(self, dto: NotionTenantDTO) -> Tenant:
        return Tenant(
            first_name=dto.prenom,
            last_name=dto.nom,
            email=dto.email,
            phone_number=dto.telephone,
            address=Address(
                street=dto.adresse_postale,
                city=dto.ville,
                postal_code=dto.code_postal
            )
        )
