from typing import Dict
from datetime import date

from src.domain.entities.lease import Lease
from src.domain.entities.value_objects import Period
from src.adapters.mappers.tenant_mapper import map_tenant
from src.adapters.mappers.guarantor_mapper import map_guarantor
from src.adapters.mappers.property_mapper import map_properties
from src.adapters.mappers.room_mapper import map_rooms
from src.adapters.mappers.rent_mapper import map_rents
from src.adapters.notion_helper import extract_property_value

def build_lease(
    loc_data,
    raw_data: Dict[str, Dict],
) -> Lease:
    """
    Build a Lease aggregate from Notion data and pre-fetched related entity maps.
    """
    props = loc_data['properties']
    
    # 1. Build Tenant
    tenant = map_tenant(loc_data)
    if not tenant:
        raise ValueError(f"Tenant mapping failed for locataire {loc_data.get('id', 'unknown')}")

    # 2. Identify Relations
    garant_ids = extract_property_value(props, "🪙 Garants") or []
    bien_ids = extract_property_value(props, "🏠 Biens") or []
    chambre_ids = extract_property_value(props, "🛏️ Chambres") or []
    loyer_ids = extract_property_value(props, "💲 Loyers") or []

    # 3. Build per-lease scoped maps from raw related data
    per_lease_raw = _build_per_lease_raw_data(raw_data, garant_ids, bien_ids, chambre_ids, loyer_ids)
    guarantors_raw = per_lease_raw['garants']
    properties_map = map_properties(per_lease_raw['bien'])
    rooms_map = map_rooms(per_lease_raw['chambres'])
    rents_map = map_rents(per_lease_raw['loyer'])

    # 4. Retrieve Related Entities
    lease_property = properties_map.get(bien_ids[0]) if bien_ids else None
    lease_room = rooms_map.get(chambre_ids[0]) if chambre_ids else None
    
    if not bien_ids or lease_property is None:
        raise ValueError(f"Missing or unresolved property for locataire {loc_data.get('id', 'unknown')}")
    if not chambre_ids or lease_room is None:
        raise ValueError(f"Missing or unresolved room for locataire {loc_data.get('id', 'unknown')}")

    # Extract Arrival/Departure Info directly from Notion properties
    jour_arrivee = extract_property_value(props, "JourArrivee")
    mois_arrivee = extract_property_value(props, "MoisArrivee")
    annee_arrivee = extract_property_value(props, "AnneeArrivee")
    
    # Type Garantie — raw string, used to dispatch guarantor subtype
    type_gar_str = extract_property_value(props, "Garantie")

    # Type Bail
    type_bail_str = extract_property_value(props, "TypeDeBail") or ""

    date_fin_theorique = extract_property_value(props, "DateFinTheorique") or ""
    mention_speciale = extract_property_value(props, "MentionSpeciale") or ""

    if not type_bail_str:
        raise ValueError(f"Missing TypeDeBail for locataire {loc_data.get('id', 'unknown')}")

    if not date_fin_theorique:
        raise ValueError(f"Missing DateFinTheorique for locataire {loc_data.get('id', 'unknown')}")

    if not annee_arrivee: annee_arrivee = 2026  # Default fallback

    # 5. Base Financials (raw loyer/charges from Notion — prorata is computed later in the use case)
    base_financials = None
    if loyer_ids and loyer_ids[0] in rents_map:
        base_financials = rents_map[loyer_ids[0]]

    # 6. Handle Guarantor — delegate to guarantor_mapper
    lease_guarantor = map_guarantor(props, type_gar_str, garant_ids, guarantors_raw)
    
    if base_financials is None:
        raise ValueError(f"Missing or unresolved loyer for locataire {loc_data.get('id', 'unknown')}")

    if lease_guarantor is None:
        raise ValueError(f"Missing or unresolved guarantor for locataire {loc_data.get('id', 'unknown')}")

    # 7. Construct Period
    start_date = None
    end_date = None
    MONTHS = {"Janvier":1, "Février":2, "Mars":3, "Avril":4, "Mai":5, "Juin":6, 
              "Juillet":7, "Août":8, "Septembre":9, "Octobre":10, "Novembre":11, "Décembre":12}
    
    if mois_arrivee:
        m_num = MONTHS.get(mois_arrivee, 1)
        try:
            start_date = date(annee_arrivee, m_num, jour_arrivee if jour_arrivee else 1)
        except:
            pass
            
    # Try to parse date_fin_theorique for end_date if it looks like a date
    if date_fin_theorique:
        # Assuming DD/MM/YYYY format
        try:
            parts = date_fin_theorique.split('/')
            if len(parts) == 3:
                end_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
        except:
            pass

    period = Period(start_date=start_date, end_date=end_date)

    # 8. Build Lease
    builder = Lease.Builder()\
        .with_id(loc_data['id'])\
        .with_tenant(tenant)\
        .with_period(period)\
        .with_type_bail(type_bail_str)\
        .with_date_fin_theorique(date_fin_theorique)\
        .with_mention_speciale(mention_speciale)
        
    if lease_guarantor: builder.with_guarantor(lease_guarantor)
    if lease_property: builder.with_property(lease_property)
    if lease_room: builder.with_room(lease_room)
    if base_financials: builder.with_financials(base_financials)

    return builder.build()


def _build_per_lease_raw_data(
    raw_data: Dict[str, Dict],
    garant_ids,
    bien_ids,
    chambre_ids,
    loyer_ids,
) -> Dict[str, Dict]:
    """Return tenant-scoped raw Notion payloads so each lease builds its own maps."""

    def _filter_results(raw_db: Dict, accepted_ids) -> Dict:
        accepted = set(accepted_ids)
        return {
            'results': [
                item
                for item in raw_db.get('results', [])
                if item.get('id') in accepted
            ]
        }

    return {
        'garants': _filter_results(raw_data.get('garants', {}), garant_ids),
        'bien': _filter_results(raw_data.get('bien', {}), bien_ids),
        'chambres': _filter_results(raw_data.get('chambres', {}), chambre_ids),
        'loyer': _filter_results(raw_data.get('loyer', {}), loyer_ids),
    }
