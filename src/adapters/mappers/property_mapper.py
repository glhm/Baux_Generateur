from typing import Dict
from src.domain.entities.property import Property
from src.adapters.notion_helper import extract_property_value


def map_properties(raw_biens) -> Dict[str, Property]:
    """Map raw Notion property/bien data to a dict of Property entities keyed by Notion ID."""
    mapping = {}
    for item in raw_biens.get('results', []):
        props = item['properties']
        p_id = item['id']

        builder = Property.Builder()\
            .with_id(p_id)\
            .with_address(extract_property_value(props, "{ADRESSE_BIEN}"))\
            .with_owner_name(extract_property_value(props, "{NOM_BAILLEUR}"))\
            .with_owner_address(extract_property_value(props, "{ADRESSE_BAILLEUR}"))\
            .with_construction_year(extract_property_value(props, "{ANNEE_CONSTRUCTION}"))\
            .with_total_surface(extract_property_value(props, "{SURFACE_TOTALE}")) # This maps to helper extract -> returns str usually

        # Removed .with_city, .with_postal_code calls
        
        mapping[p_id] = builder.build()
    return mapping
