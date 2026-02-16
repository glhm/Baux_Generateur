from typing import Optional

from src.adapters.notion_helper import extract_property_value
from src.domain.entities.tenant import Tenant


def map_tenant(loc_data) -> Optional[Tenant]:
    """Build a Tenant entity from raw Notion locataire data."""
    props = loc_data["properties"]

    nom = extract_property_value(props, "{NOM_LOCATAIRE}")
    if not nom:
        return None

    years = [y["name"] for y in props.get("ANNEES", {}).get("multi_select", [])]

    builder = (
        Tenant.Builder()
        .with_nom(nom)
        .with_email(extract_property_value(props, "{MAIL}") or "")
        .with_naissance(
            extract_property_value(props, "{DATE_NAISSANCE}") or "",
            extract_property_value(props, "{LIEU_NAISSANCE}") or "",
        )
        .with_envoyer_quittance(bool(extract_property_value(props, "EnvoyerQuittance")))
        .with_activer_generation(bool(extract_property_value(props, "ActiverGeneration")))
        .with_activer_generation_quittances(bool(extract_property_value(props, "ActiverGenerationQuittances")))
        .with_statut_envoi_quittance(extract_property_value(props, "StatutEnvoiQuittance") or "")
        .with_years(years)
    )

    return builder.build()
