from typing import Dict
from src.domain.entities.financials import Numbers
from src.adapters.notion_helper import extract_property_value


def map_rents(raw_loyers) -> Dict[str, Numbers]:
    """Map raw Notion rent/loyer data to a dict of Numbers entities keyed by Notion ID."""
    mapping = {}
    for item in raw_loyers.get('results', []):
        props = item['properties']
        l_id = item['id']

        rent = extract_property_value(props, "{MONTANT_LOYER}") or extract_property_value(props, "{LOYER_HC}")
        charges = extract_property_value(props, "{MONTANT_CHARGES}") or extract_property_value(props, "{CHARGES}")
        deposit = extract_property_value(props, "{DEPOT_GARANTIE}")

        builder = Numbers.Builder()\
            .with_rent(float(rent) if rent else 0.0)\
            .with_charges(float(charges) if charges else 0.0)\
            .with_deposit(float(deposit) if deposit else 0.0)

        mapping[l_id] = builder.build()
    return mapping
