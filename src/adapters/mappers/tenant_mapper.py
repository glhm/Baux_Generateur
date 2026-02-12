from typing import Dict, Optional
from src.domain.entities.tenant import Tenant
from src.adapters.notion_helper import extract_property_value
from src.domain.enums import LeaseType, GuarantorType

def map_tenant(loc_data) -> Optional[Tenant]:
    """Build a Tenant entity (personal info only) from raw Notion locataire data."""
    props = loc_data['properties']
    
    # Required fields
    nom = extract_property_value(props, "{NOM_LOCATAIRE}")
    if not nom: 
        return None


    


    # Builder or Direct? Tenant has Builder in Step 249.
    builder = Tenant.Builder()\
        .with_nom(nom)\
        .with_email(extract_property_value(props, "{MAIL}"))\
        .with_naissance(
            extract_property_value(props, "{DATE_NAISSANCE}"),
            extract_property_value(props, "{LIEU_NAISSANCE}")
        )\
        .with_envoyer_quittance(extract_property_value(props, "EnvoyerQuittance"))\
        .with_activer_generation(extract_property_value(props, "ActiverGeneration"))\
        .with_activer_generation_quittances(extract_property_value(props, "ActiverGenerationQuittances"))\
        .with_statut_envoi_quittance(extract_property_value(props, "StatutEnvoiQuittance") or "") \
        .with_years([y['name'] for y in props.get('ANNEES', {}).get('multi_select', [])])

    return builder.build()
