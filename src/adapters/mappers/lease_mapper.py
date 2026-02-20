from typing import Dict, Optional, List
from datetime import date
from src.domain.entities.lease import Lease
from src.domain.entities.tenant import Tenant
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.financials import Financials
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.value_objects import Period
from src.adapters.mappers.tenant_mapper import map_tenant
from src.adapters.mappers.guarantor_mapper import map_guarantor_for_lease
from src.adapters.notion_helper import extract_property_value

def build_lease(
    loc_data,
    guarantors_map: Dict[str, Guarantor],
    properties_map: Dict[str, Property],
    rooms_map: Dict[str, Room],
    rents_map: Dict[str, Financials]
) -> Optional[Lease]:
    """
    Build a Lease aggregate from Notion data and pre-fetched related entity maps.
    """
    props = loc_data['properties']
    
    # 1. Build Tenant
    tenant = map_tenant(loc_data)
    if not tenant:
        return None

    # 2. Identify Relations
    garant_ids = extract_property_value(props, "🪙 Garants") or []
    bien_ids = extract_property_value(props, "🏠 Biens") or []
    chambre_ids = extract_property_value(props, "🛏️ Chambres") or []
    loyer_ids = extract_property_value(props, "💲 Loyers") or []

    # 3. Retrieve Related Entities
    lease_property = properties_map.get(bien_ids[0]) if bien_ids else None
    lease_room = rooms_map.get(chambre_ids[0]) if chambre_ids else None
    
    # Extract Arrival/Departure Info directly from Notion properties
    jour_arrivee = extract_property_value(props, "JourArrivee")
    mois_arrivee = extract_property_value(props, "MoisArrivee")
    annee_arrivee = extract_property_value(props, "AnneeArrivee")
    
    # Handle ANNEES override for AnneeArrivee (legacy logic)
    annees = extract_property_value(props, "ANNEES")
    if annees and isinstance(annees, list) and len(annees) > 0:
        try:
            annee_arrivee = int(annees[0])
        except ValueError:
            pass

    # Type Garantie — raw string, used to dispatch guarantor subtype
    type_gar_str = extract_property_value(props, "Garantie")

    # Type Bail
    type_bail_str = extract_property_value(props, "TypeDeBail") or ""

    date_fin_theorique = extract_property_value(props, "DateFinTheorique") or ""
    mention_speciale = extract_property_value(props, "MentionSpeciale") or ""

    if not annee_arrivee: annee_arrivee = 2026  # Default fallback

    # 4. Base Financials (raw loyer/charges from Notion — prorata is computed later in the use case)
    base_financials = None
    if loyer_ids and loyer_ids[0] in rents_map:
        base_financials = rents_map[loyer_ids[0]]

    # 5. Handle Guarantor — delegate to guarantor_mapper
    lease_guarantor = map_guarantor_for_lease(
        props, type_gar_str, garant_ids, guarantors_map
    )
    
    # 6. Construct Period
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

    # 7. Build Lease
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

    try:
        return builder.build()
    except ValueError:
        return None
