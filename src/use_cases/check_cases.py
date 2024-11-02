def is_lease_generation_enabled(locataire):
    return locataire['properties'].get('ActiverGeneration', {}).get('checkbox', False)

def is_receipts_generation_enabled(locataire):
    return locataire['properties'].get('ActiverGenerationQuittances', {}).get('checkbox', False)

def is_quittance_sending_enabled(locataire):
    return locataire['properties'].get('EnvoyerQuittance', {}).get('checkbox', False)
