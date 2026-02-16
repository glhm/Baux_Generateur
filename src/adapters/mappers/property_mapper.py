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
            .with_address(extract_property_value(props, "{ADRESSE_LOGEMENT}"))\
            .with_designation(extract_property_value(props, "{DESIGNATION_BIEN}"))\
            .with_type_habitat(extract_property_value(props, "{TYPE_BIEN}"))\
            .with_regime_juridique(extract_property_value(props, "{REGIME_JURIDIQUE}"))\
            .with_surface_habitable(extract_property_value(props, "{SURFACE_HABITABLE}"))\
            .with_date_construction(extract_property_value(props, "{DATE_CONSTRUCTION}"))\
            .with_nombre_pieces(extract_property_value(props, "{NOMBRE_PIECES}"))\
            .with_enumeration_communs(extract_property_value(props, "{ENUMERATION_COMMUNS}"))\
            .with_autres_parties(extract_property_value(props, "{AUTRES_PARTIES_LOGEMENT}"))\
            .with_dpe(extract_property_value(props, "{DPE}"))\
            .with_elements_equipement_logement(extract_property_value(props, "{ELEMENTS_EQUIPEMENT_LOGEMENT}"))\
            .with_modalites(extract_property_value(props, "{MODALITE_CHAUFFAGE}"), extract_property_value(props, "{MODALITE_EAU}"))
        mapping[p_id] = builder.build()
    return mapping
