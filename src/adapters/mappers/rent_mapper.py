from typing import Dict

from src.adapters.notion_helper import extract_property_value
from src.domain.entities.financials import Financials


def map_rents(raw_loyers) -> Dict[str, Financials]:
    """Map raw Notion rent/loyer data to Financials base amounts keyed by Notion ID."""
    mapping = {}
    for item in raw_loyers.get('results', []):
        props = item['properties']
        l_id = item['id']

        rent = extract_property_value(props, "{MONTANT_LOYER}") 
        charges = extract_property_value(props, "{MONTANT_CHARGES}") 
#loyer les données a recuperer c'est {MONTANT_LOYER} {MONTANT_CHARGES} {MONTANT_TOTAL_LETTRES} {ASSAINISSEMENT} {EAU} {CHAUFFAGE} {ELECTRICITE} {WIFI} {MENAGE}

        mapping[l_id] = Financials.from_base_amounts(
            loyer_amount=float(rent) if rent else 0.0,
            charges_amount=float(charges) if charges else 0.0,
        )

    return mapping
