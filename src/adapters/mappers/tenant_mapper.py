from typing import Dict, Optional
from src.domain.entities.tenant import Tenant
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.financials import Numbers
from src.adapters.notion_helper import extract_property_value


def build_tenant(
    loc_data,
    guarantors_map: Dict[str, Guarantor],
    properties_map: Dict[str, Property],
    rooms_map: Dict[str, Room],
    rents_map: Dict[str, Numbers]
) -> Optional[Tenant]:
    """Build a Tenant entity from raw Notion locataire data and related entity maps."""
    props = loc_data['properties']

    # Identify relations
    garant_ids = extract_property_value(props, "🪙 Garants") or []
    bien_ids = extract_property_value(props, "🏠 Biens") or []
    chambre_ids = extract_property_value(props, "🛏️ Chambres") or []
    loyer_ids = extract_property_value(props, "💲 Loyers") or []

    # Build base Tenant
    builder = Tenant.Builder()\
        .with_nom(extract_property_value(props, "{NOM_LOCATAIRE}"))\
        .with_envoyer_quittance(extract_property_value(props, "EnvoyerQuittance"))\
        .with_activer_generation(extract_property_value(props, "ActiverGeneration"))\
        .with_email(extract_property_value(props, "{MAIL}"))\
        .with_type_bail(extract_property_value(props, "TypeDeBail"))\
        .with_type_garantie(extract_property_value(props, "Garantie"))\
        .with_naissance(
            extract_property_value(props, "{DATE_NAISSANCE}"),
            extract_property_value(props, "{LIEU_NAISSANCE}")
        )\
        .with_arrivee(
            extract_property_value(props, "{JOUR_ARRIVEE}"),
            extract_property_value(props, "{MOIS_ARRIVEE}"),
            2026  # TODO: Extract from '{ANNEES}' text/multiselect
        )

    # Years handling
    annees = extract_property_value(props, "ANNEES")
    if annees:
        builder.with_annees(annees)
        try:
            builder.with_arrivee(
                extract_property_value(props, "{JOUR_ARRIVEE}"),
                extract_property_value(props, "{MOIS_ARRIVEE}"),
                int(annees[0]) if annees else 2026
            )
        except:
            pass

    # Attach related entities
    if garant_ids:
        gs = [guarantors_map[gid] for gid in garant_ids if gid in guarantors_map]
        builder.with_guarantors(gs)

    if bien_ids and bien_ids[0] in properties_map:
        builder.with_property(properties_map[bien_ids[0]])

    if chambre_ids and chambre_ids[0] in rooms_map:
        builder.with_room(rooms_map[chambre_ids[0]])

    if loyer_ids and loyer_ids[0] in rents_map:
        builder.with_financials(rents_map[loyer_ids[0]])

    return builder.build()
