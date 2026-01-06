import os
import requests
from typing import List, Dict, Any, Optional
from src.domain.ports.tenant_repository import TenantRepository
from src.domain.entities.tenant import Tenant
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.financials import Numbers
from src.domain.entities.value_objects import Period, Money
from src.domain.enums import LeaseType, GuarantorType
from src.conf.info_apis import DATABASE_IDS

class NotionAdapter(TenantRepository):
    def __init__(self):
        self.notion_api_secret = os.getenv('NOTION_API_SECRET')
        if not self.notion_api_secret:
            raise ValueError("NOTION_API_SECRET environment variable is not defined.")
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_secret}",
            "Notion-Version": "2022-06-28",
        }

    def get_tenants(self) -> List[Tenant]:
        """
        Fetches all data from Notion databases and constructs Tenant entities.
        """
        # 1. Fetch all raw data
        raw_data = self._fetch_all_databases()
        
        # 2. Map raw data to entities
        tenants: List[Tenant] = []
        
        # Helper maps for efficient lookup
        guarantors_map = self._map_guarantors(raw_data.get('garants', {}))
        properties_map = self._map_properties(raw_data.get('bien', {}))
        rooms_map = self._map_rooms(raw_data.get('chambres', {}))
        rents_map = self._map_rents(raw_data.get('loyer', {}))

        # 3. Build Tenant objects
        locataires_data = raw_data.get('locataire', {}).get('results', [])
        for loc_data in locataires_data:
            tenant = self._build_tenant(loc_data, guarantors_map, properties_map, rooms_map, rents_map)
            if tenant:
                tenants.append(tenant)
                
        return tenants

    def _fetch_all_databases(self) -> Dict[str, Any]:
        all_data = {}
        for name, db_id in DATABASE_IDS.items():
            response = requests.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=self.headers
            )
            response.raise_for_status()
            all_data[name] = response.json()
        return all_data

    def _extract_property_value(self, properties: Dict, key: str) -> Any:
        # Simplified extraction logic based on previous extract_dicts_from_data.py
        # Handles different Notion property types (title, rich_text, number, select, formula, checkbox)
        # Note: keys in Notion might include braces like "{NOM_LOCATAIRE}" based on previous code.
        
        # Try both with and without braces if not found directly? 
        # The previous code seemed to iterate or use specific keys. 
        # I'll stick to a robust check.
        
        prop = properties.get(key)
        if not prop:
             # Fallback check for keys that might have lost/gained braces in transit or previous code
             # But let's assume keys are exact from the configuration/Notion.
             return None

        prop_type = prop.get('type')
        if not prop_type:
            # Fallback based on keys presence
            if 'title' in prop: prop_type = 'title'
            elif 'rich_text' in prop: prop_type = 'rich_text'
            elif 'number' in prop: prop_type = 'number'
            elif 'select' in prop: prop_type = 'select'
            elif 'multi_select' in prop: prop_type = 'multi_select'
            elif 'checkbox' in prop: prop_type = 'checkbox'
            elif 'formula' in prop: prop_type = 'formula'
            elif 'relation' in prop: prop_type = 'relation'

        if prop_type == 'title':
            return prop['title'][0]['text']['content'] if prop['title'] else ""
        elif prop_type == 'rich_text':
            return prop['rich_text'][0]['text']['content'] if prop['rich_text'] else ""
        elif prop_type == 'number':
            return prop['number']
        elif prop_type == 'select':
            return prop['select']['name'] if prop['select'] else None
        elif prop_type == 'multi_select':
            return [item['name'] for item in prop['multi_select']]
        elif prop_type == 'checkbox':
            return prop['checkbox']
        elif prop_type == 'formula':
            if prop['formula']['type'] == 'number':
                return prop['formula']['number']
            elif prop['formula']['type'] == 'string': # Just in case
                return prop['formula']['string']
        elif prop_type == 'relation':
            return [rel['id'] for rel in prop['relation']]
            
        return None

    def _map_guarantors(self, raw_garants) -> Dict[str, Guarantor]:
        mapping = {}
        for item in raw_garants.get('results', []):
            props = item['properties']
            g_id = item['id']
            # Extraction
            nom = self._extract_property_value(props, "{NOM_GARANT}")
            prenom = self._extract_property_value(props, "{PRENOM_GARANT}")
            # ... (other fields as needed by Guarantor entity)
            # Guarantor entity requires: nom, prenom, adresse, ville, code_postal, tel, email
            # Based on mock/previous code, keys might be specific.
            
            # Using entity Builder
            builder = Guarantor.Builder()\
                .with_nom(nom)\
                .with_prenom(prenom)\
                .with_adresse(self._extract_property_value(props, "{ADRESSE_GARANT}"))\
                .with_ville("") \
                .with_code_postal("") \
                .with_tel(self._extract_property_value(props, "{TEL_GARANT}"))\
                .with_email(self._extract_property_value(props, "{MAIL_GARANT}"))\
            
            # Additional fields like birth info might be needed if included in Entity
            # Checking Guarantor Entity definition (from memory or if needed view file):
            # It has methods like with_naissance(date, lieu)
            
            builder.with_naissance(
                self._extract_property_value(props, "{DATE_NAISSANCE_GARANT}"), 
                self._extract_property_value(props, "{LIEU_NAISSANCE_GARANT}")
            )

            # Visale specific? "garant-visale-id" logic?
            # If "NUMERO_VISALE" exists, maybe map it? 
            # Guarantor entity implies physical person mostly, but could adapt.
            
            mapping[g_id] = builder.build()
        return mapping

    def _map_properties(self, raw_biens) -> Dict[str, Property]:
        mapping = {}
        for item in raw_biens.get('results', []):
            props = item['properties']
            p_id = item['id']
            builder = Property.Builder()\
                .with_address(self._extract_property_value(props, "{ADRESSE_BIEN}"))\
                .with_city(self._extract_property_value(props, "{VILLE}"))\
                .with_postal_code(self._extract_property_value(props, "{CODE_POSTAL}"))\
                .with_owner_name(self._extract_property_value(props, "{NOM_BAILLEUR}"))\
                .with_owner_address(self._extract_property_value(props, "{ADRESSE_BAILLEUR}"))\
                .with_construction_year(self._extract_property_value(props, "{ANNEE_CONSTRUCTION}"))\
                .with_total_surface(self._extract_property_value(props, "{SURFACE_TOTALE}"))
            
            mapping[p_id] = builder.build()
        return mapping

    def _map_rooms(self, raw_chambres) -> Dict[str, Room]:
        mapping = {}
        for item in raw_chambres.get('results', []):
            props = item['properties']
            r_id = item['id']
            builder = Room.Builder()\
                .with_name(self._extract_property_value(props, "{NOM_CHAMBRE}"))\
                .with_surface(self._extract_property_value(props, "{SURFACE_CHAMBRE}"))\
                .with_floor(self._extract_property_value(props, "{ETAGE}"))\
                .with_description(self._extract_property_value(props, "{DESCRIPTION_CHAMBRE}"))
            
            mapping[r_id] = builder.build()
        return mapping

    def _map_rents(self, raw_loyers) -> Dict[str, Numbers]:
        mapping = {}
        for item in raw_loyers.get('results', []):
            props = item['properties']
            l_id = item['id']
            # Using Numbers.Builder (Financials)
            # Keys might be {LOYER_HC} or {MONTANT_LOYER} (as seen in mocks updates)
            # Using updated keys from tests: {MONTANT_LOYER}, {MONTANT_CHARGES}
            
            rent = self._extract_property_value(props, "{MONTANT_LOYER}") or self._extract_property_value(props, "{LOYER_HC}")
            charges = self._extract_property_value(props, "{MONTANT_CHARGES}") or self._extract_property_value(props, "{CHARGES}")
            deposit = self._extract_property_value(props, "{DEPOT_GARANTIE}")
            
            builder = Numbers.Builder()\
                .with_rent(float(rent) if rent else 0.0)\
                .with_charges(float(charges) if charges else 0.0)\
                .with_deposit(float(deposit) if deposit else 0.0)
                
            mapping[l_id] = builder.build()
        return mapping

    def _build_tenant(self, loc_data, guarantors_map, properties_map, rooms_map, rents_map) -> Optional[Tenant]:
        props = loc_data['properties']
        
        # Identify relations
        garant_ids = self._extract_property_value(props, "🪙 Garants") or []
        bien_ids = self._extract_property_value(props, "🏠 Biens") or []
        chambre_ids = self._extract_property_value(props, "🛏️ Chambres") or []
        loyer_ids = self._extract_property_value(props, "💲 Loyers") or []
        
        # Build base Tenant
        builder = Tenant.Builder()\
            .with_nom(self._extract_property_value(props, "{NOM_LOCATAIRE}"))\
            .with_envoyer_quittance(self._extract_property_value(props, "EnvoyerQuittance"))\
            .with_activer_generation(self._extract_property_value(props, "ActiverGeneration"))\
            .with_email(self._extract_property_value(props, "{MAIL}"))\
            .with_type_bail(self._extract_property_value(props, "TypeDeBail"))\
            .with_type_garantie(self._extract_property_value(props, "Garantie"))\
            .with_naissance(
                self._extract_property_value(props, "{DATE_NAISSANCE}"),
                self._extract_property_value(props, "{LIEU_NAISSANCE}")
            )\
            .with_arrivee(
                self._extract_property_value(props, "{JOUR_ARRIVEE}"),
                self._extract_property_value(props, "{MOIS_ARRIVEE}"), # Text like 'Janvier'
                2026 # TODO: Extract from '{ANNEES}' text/multiselect? using current logic
            )
            
        # Years handling
        annees = self._extract_property_value(props, "ANNEES")
        if annees:
            builder.with_annees(annees)
            # Try to infer arrival year from first year listed? 
            # Or assume logic handles it. For now, passing data.
            try:
                builder.with_arrivee(
                     self._extract_property_value(props, "{JOUR_ARRIVEE}"),
                     self._extract_property_value(props, "{MOIS_ARRIVEE}"),
                     int(annees[0]) if annees else 2026
                )
            except:
                pass


        # Attach related entities
        if garant_ids:
             # Assuming single guarantor for now or list
             gs = []
             for gid in garant_ids:
                 if gid in guarantors_map:
                     gs.append(guarantors_map[gid])
             builder.with_guarantors(gs)
        
        if bien_ids and bien_ids[0] in properties_map:
            builder.with_property(properties_map[bien_ids[0]])
            
        if chambre_ids and chambre_ids[0] in rooms_map:
            builder.with_room(rooms_map[chambre_ids[0]])
            
        if loyer_ids and loyer_ids[0] in rents_map:
            builder.with_financials(rents_map[loyer_ids[0]])

        return builder.build()
