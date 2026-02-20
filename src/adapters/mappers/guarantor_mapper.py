from typing import Dict, Optional, List
from src.domain.entities.guarantor import Guarantor, PhysicalGuarantor, VisaleGuarantor
from src.adapters.notion_helper import extract_property_value


def map_guarantors(raw_garants) -> Dict[str, PhysicalGuarantor]:
    """Map raw Notion guarantor data to a dict of PhysicalGuarantor entities keyed by Notion ID."""
    mapping = {}
    for item in raw_garants.get('results', []):
        props = item['properties']
        g_id = item['id']

        mapping[g_id] = PhysicalGuarantor(
            full_name_raw=extract_property_value(props, "{NOM_GARANT}"),
            email=extract_property_value(props, "{MAIL_GARANT}"),
            phone_number=extract_property_value(props, "{TEL_GARANT}"),
            address_raw=extract_property_value(props, "{ADRESSE_GARANT}"),
            date_naissance=extract_property_value(props, "{DATE_NAISSANCE_GARANT}"),
            lieu_naissance=extract_property_value(props, "{LIEU_NAISSANCE_GARANT}"),
        )

    return mapping


def map_guarantor_for_lease(
    props: dict,
    type_garantie_str: Optional[str],
    garant_ids: List[str],
    guarantors_map: Dict[str, Guarantor],
) -> Optional[Guarantor]:
    """
    Build the correct Guarantor subtype for a lease based on the Notion
    'Garantie' property value.

    - 'Visale' -> VisaleGuarantor (built from tenant/lease Notion properties)
    - anything else -> PhysicalGuarantor (looked up from the pre-fetched guarantors_map)
    """
    if type_garantie_str == "Visale":
        return VisaleGuarantor(
            numero_visale=extract_property_value(props, "{N_VISALE}"),
            numero_contrat_visale=extract_property_value(props, "{N_CONTRAT_VISALE}"),
            date_emission_visale=extract_property_value(props, "{DATE_EMISSION_VISALE}"),
        )

    # Physical Guarantor — take the first one if available
    if garant_ids:
        gid = garant_ids[0]
        return guarantors_map.get(gid)

    return None
