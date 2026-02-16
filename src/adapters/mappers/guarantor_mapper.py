from typing import Dict
from src.domain.entities.guarantor import PhysicalGuarantor
from src.adapters.notion_helper import extract_property_value


def map_guarantors(raw_garants) -> Dict[str, PhysicalGuarantor]:
    """Map raw Notion guarantor data to a dict of PhysicalGuarantor entities keyed by Notion ID."""
    mapping = {}
    for item in raw_garants.get('results', []):
        props = item['properties']
        g_id = item['id']

        # Manual construction or Builder if we kept it? 
        # I removed Builder in the Entity rewrite earlier for simpler dataclass usage? 
        # Wait, I rewrote Guarantor.py but I might have removed the Builder if I used dataclass directly.
        # Let's check the file content I wrote in Step 250.
        # I did not include a Builder in Step 250's inheritence code?
        # Let's assume I need to construct it directly or check if I need to add Builder back.
        # Actually, for PhysicalGuarantor I can just construct it.
        
        mapping[g_id] = PhysicalGuarantor(
            full_namew=extract_property_value(props, "{NOM_GARANT}"),
            email=extract_property_value(props, "{MAIL_GARANT}"),
            phone_number=extract_property_value(props, "{TEL_GARANT}"),
            address_raw=extract_property_value(props, "{ADRESSE_GARANT}"),
            date_naissance=extract_property_value(props, "{DATE_NAISSANCE_GARANT}"),
            lieu_naissance=extract_property_value(props, "{LIEU_NAISSANCE_GARANT}"),
        )

    return mapping
