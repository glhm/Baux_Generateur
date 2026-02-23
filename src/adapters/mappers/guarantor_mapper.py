from typing import Optional, List, Dict, Any

from src.adapters.notion_helper import extract_property_value
from src.domain.entities.guarantor import Guarantor, PhysicalGuarantor, VisaleGuarantor


def map_guarantor(
    props: Dict[str, Any],
    type_garantie_str: Optional[str],
    garant_ids: List[str],
    raw_garants: Dict[str, Any],
) -> Optional[Guarantor]:
    """
    Build the correct Guarantor subtype for a lease.

    - Visale: built directly from tenant page properties.
    - Physical: looked up from raw guarantor pages by relation ID.
    """
    if type_garantie_str == "Visale":
        return VisaleGuarantor(
            numero_visale=extract_property_value(props, "{N_VISALE}"),
            numero_contrat_visale=extract_property_value(props, "{N_CONTRAT_VISALE}"),
            date_emission_visale=extract_property_value(props, "{DATE_EMISSION_VISALE}"),
        )

    if not garant_ids:
        return None

    target_id = garant_ids[0]
    for item in raw_garants.get('results', []):
        if item.get('id') != target_id:
            continue

        guarantor_props = item.get('properties', {})
        return PhysicalGuarantor(
            full_name_raw=extract_property_value(guarantor_props, "{NOM_GARANT}"),
            email=extract_property_value(guarantor_props, "{MAIL_GARANT}"),
            phone_number=extract_property_value(guarantor_props, "{TEL_GARANT}"),
            address_raw=extract_property_value(guarantor_props, "{ADRESSE_GARANT}"),
            date_naissance=extract_property_value(guarantor_props, "{DATE_NAISSANCE_GARANT}"),
            lieu_naissance=extract_property_value(guarantor_props, "{LIEU_NAISSANCE_GARANT}"),
        )

    return None
