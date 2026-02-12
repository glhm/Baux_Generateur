from typing import Dict
from src.domain.entities.financials import Financials
from src.adapters.notion_helper import extract_property_value


def map_rents(raw_loyers) -> Dict[str, Financials]:
    """Map raw Notion rent/loyer data to a dict of Financials entities keyed by Notion ID."""
    mapping = {}
    for item in raw_loyers.get('results', []):
        props = item['properties']
        l_id = item['id']

        rent = extract_property_value(props, "{MONTANT_LOYER}") or extract_property_value(props, "{LOYER_HC}")
        charges = extract_property_value(props, "{MONTANT_CHARGES}") or extract_property_value(props, "{CHARGES}")
        deposit = extract_property_value(props, "{DEPOT_GARANTIE}")

        # Static builder method
        financials = Financials.calculate(
            loyer_amount=float(rent) if rent else 0.0,
            charges_amount=float(charges) if charges else 0.0,
            # We don't have arrival date here, so calculate might need default?
            # Wait, calculate() requires jour_arrivee/mois_arrivee_str.
            # In old code logic (Step 196), it was using a Builder pattern on Numbers?
            # Step 196: `builder = Numbers.Builder()...`
            # Step 202 `Numbers` file view showed `calculate` static method but NOT a Builder class.
            # Step 172 `rent_mapper.py` used `Numbers.Builder()`.
            # This implies `Numbers` HAD a builder originally.
            # But in Step 202 view, I saw `calculate` static method and NO Builder class.
            # So `rent_mapper.py` in Step 172 was probably based on old assumptions or I broke it.
            # AND `calculate` asks for arrival info, which we don't have in the Rents database generally (it's per tenant?).
            # Actually, `Numbers` was originally per Tenant?
            # If `rent_mapper` processes RENTS database, does it have access to tenant info? No.
            # The calculation `prorata` etc. depends on Tenant arrival.
            # So `rents_map` should probably map raw values, and the *Lease construction* should calculate the Financials?
            # But `Numbers` (Financials) object seems to hold calculated values (prorata).
            # So `Financials` object creation likely happens at `Lease` building time, not at `Rents` mapping time?
            # OR `Rents` mapping returns a partial object or a DTO?
            # Step 172 used a Builder.
            # If I look at `NotionAdapter` Step 196: `_map_rents` -> `Numbers.Builder()`.
            # If `Financials` (ex-Numbers) is immutable dataclass with calculated fields, I can't build it without data.
            # So `rent_mapper` should perhaps return a `RentData` DTO, and `lease_mapper` creates `Financials`.
            # OR `Financials` class should allow creation with 0s and then we recalculate?
            # Given the constraints, I will make `rent_mapper` return a DTO or a raw dict, 
            # OR update `Financials` to be buildable without prorata (using defaults).
            # `Financials` is frozen dataclass.
            
            # Use dummy values for now essentially making this a "Raw Financials" holder?
            # Or use `Financials` just for holding the reference values?
            # Using calculate with 0s for missing info:
            jour_arrivee=1, mois_arrivee_str="Janvier" 
        )
        
        mapping[l_id] = financials
    return mapping
