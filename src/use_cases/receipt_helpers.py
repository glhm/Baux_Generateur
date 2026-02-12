from typing import List, Dict, Any, Optional

# Strings for receipts
TITRE_DETAIL_REGLEMENT = "Détail du règlement :"
PARAGRAPHE_DETAIL_PREMIER_MOIS = "Le locataire étant entré dans les lieux en cours de mois, le loyer et les charges ont été calculés au prorata temporis."
PARAGRAPHE_DETAIL_DERNIER_MOIS = "Le locataire ayant quitté les lieux en cours de mois, le loyer et les charges ont été calculés au prorata temporis."

def build_receipt_requests(
    somme_due: float,
    jour_debut: int,
    titre_detail: str,
    paragraphe_detail: str,
    annee: int,
    mois_nom: str,
    dernier_jour_mois: int,
    jour_fin: Optional[int] = None,
    return_dict: bool = True
) -> Dict[str, str]:
    """
    Builds the substitution dict for the receipt template.
    Refactored to return dict for compatibility with Renderer.
    """
    
    # Defaults and formatting
    jou_fin_val = jour_fin if jour_fin else dernier_jour_mois
    
    params = {
        "{{PERIODE}}": f"du {jour_debut:02} {mois_nom} {annee} au {jou_fin_val:02} {mois_nom} {annee}",
        "{{DATE_PAIEMENT}}": f"{dernier_jour_mois:02} {mois_nom} {annee}", 
        "{{SOMME_TOTALE}}": f"{somme_due:.2f}".replace('.', ','),
        "{{TITRE_DETAIL}}": titre_detail,
        "{{PARAGRAPHE_DETAIL}}": paragraphe_detail,
    }

    return params
