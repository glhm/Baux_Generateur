from typing import Dict
from src.domain.entities.guarantor import Guarantor
from src.adapters.notion_helper import extract_property_value


def map_guarantors(raw_garants) -> Dict[str, Guarantor]:
    """Map raw Notion guarantor data to a dict of Guarantor entities keyed by Notion ID."""
    mapping = {}
    for item in raw_garants.get('results', []):
        props = item['properties']
        g_id = item['id']

        builder = Guarantor.Builder()\
            .with_nom(extract_property_value(props, "{NOM_GARANT}"))\
            .with_prenom(extract_property_value(props, "{PRENOM_GARANT}"))\
            .with_adresse(extract_property_value(props, "{ADRESSE_GARANT}"))\
            .with_ville("") \
            .with_code_postal("") \
            .with_tel(extract_property_value(props, "{TEL_GARANT}"))\
            .with_email(extract_property_value(props, "{MAIL_GARANT}"))

        builder.with_naissance(
            extract_property_value(props, "{DATE_NAISSANCE_GARANT}"),
            extract_property_value(props, "{LIEU_NAISSANCE_GARANT}")
        )

        mapping[g_id] = builder.build()
    return mapping
