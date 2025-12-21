from typing import Dict, List, Any
from src.domain.entities.tenant import Tenant
from src.domain.enums import LeaseType, GuarantorType
from src.utils.number_utils import number_to_text # Assuming this util exists or I should create it

class GoogleDocMapper:
    """
    Maps Tenant entity data to Google Doc replacement requests.
    """

    @staticmethod
    def get_lease_placeholders(tenant: Tenant) -> Dict[str, str]:
        return GoogleDocMapper._build_lease_placeholders(tenant)

    @staticmethod
    def get_receipt_placeholders(tenant: Tenant, month: str, year: int) -> Dict[str, str]:
        return GoogleDocMapper._build_receipt_placeholders(tenant, month, year)

    @staticmethod
    def map_lease_requests(tenant: Tenant) -> List[Dict[str, Any]]:
        placeholders = GoogleDocMapper.get_lease_placeholders(tenant)
        return GoogleDocMapper._build_requests_from_dict(placeholders)

    @staticmethod
    def _build_lease_placeholders(tenant: Tenant) -> Dict[str, str]:
        p = {}
        
        # --- Identification et Locataire ---
        # {{TYPE_BAIL_MEUBLE}}
        # Logic: If Meublé -> "meublé", if Nu -> "non meublé"? Or specific phrasing. 
        # User prompt: "Peut être de type 'Meublé', 'Etudiant', ou 'Nu'"
        # Placeholder name suggests "MEUBLE". 
        # I'll output the string value of the Enum for now or empty if not meuble?
        # The placeholder is likely asking for the *Word* "meublé" or similar description.
        # User example: "{{TYPE_BAIL_MEUBLE}}"
        p['{{TYPE_BAIL_MEUBLE}}'] = "meublé" if tenant.type_bail == LeaseType.MEUBLE else "non meublé" # Assumption
        
        # {{LA_CAUTION}}
        # Likely the text describing the Guarantor? Or just the name?
        # User desc: "{{LA_CAUTION}}"
        # If Visale -> "Action Logement (Garantie VISALE)"
        # If Physique -> Guarantor Name(s)
        if tenant.type_garantie == GuarantorType.VISALE:
            p['{{LA_CAUTION}}'] = "Action Logement (Garantie VISALE)" 
        else:
            guarantor_names = [g.full_name for g in tenant.guarantors if not g.masquer]
            p['{{LA_CAUTION}}'] = ", ".join(guarantor_names) if guarantor_names else "Sans caution"

        p['{{NOM_LOCATAIRE}}'] = tenant.full_name
        p['{{LIEU_NAISSANCE_LOCATAIRE}}'] = tenant.lieu_naissance or ""
        p['{{DATE_NAISSANCE_LOCATAIRE}}'] = tenant.date_naissance or ""

        # --- Description du Logement ---
        prop = tenant.property_obj
        if prop:
            p['{{DESIGNATION_BIEN}}'] = prop.designation or ""
            p['{{ADRESSE_LOGEMENT}}'] = prop.address
            p['{{TYPE_HABITAT}}'] = prop.type_habitat or ""
            p['{{REGIME_JURIDIQUE}}'] = prop.regime_juridique or ""
            p['{{DATE_CONSTRUCTION}}'] = str(prop.date_construction) if prop.date_construction else ""
            p['{{SURFACE_HABITABLE}}'] = prop.surface_habitable or ""
            p['{{NOMBRE_PIECES}}'] = str(prop.nombre_pieces) if prop.nombre_pieces else ""
            p['{{AUTRES_PARTIES_LOGEMENT}}'] = prop.autres_parties or ""
            p['{{ELEMENTS_EQUIPEMENT_LOGEMENT}}'] = prop.elements_equipement or ""
            p['{{MODALITE_CHAUFFAGE}}'] = prop.modalite_chauffage or ""
            p['{{MODALITE_EAU}}'] = prop.modalite_eau or ""
        else:
            # Fallback if property is missing (should not happen in valid state)
            pass

        # --- Espaces Privatifs et Communs ---
        room = tenant.room
        if room:
            p['{{LOCALISATION}}'] = room.localisation or ""
            p['{{SURFACE_CHAMBRE}}'] = str(room.surface) if room.surface else ""
            p['{{VOLUME_HABITABLE}}'] = room.volume or ""
        
        # Communs needs logic? "ENUMERATION_COMMUNS" usually property common areas
        p['{{ENUMERATION_COMMUNS}}'] = prop.enumeration_contenu if prop else "" # Or specialized field?

        # --- Dates et Durée ---
        # {{DATE_CONTRAT}} -> Today usually? Or start date?
        # {{DATE_FIN}} -> tenant.date_fin
        # {{PARAGRAPHE_DUREE_CONTRAT}} -> Dynamic logic?
        p['{{DATE_CONTRAT}}'] = f"{tenant.jour_arrivee} {tenant.mois_arrivee} {tenant.annee_arrivee}" # Construct date string
        p['{{DATE_FIN}}'] = tenant.date_fin or ""
        
        # Duration paragraph logic based on LeaseType
        if tenant.type_bail == LeaseType.ETUDIANT:
            p['{{PARAGRAPHE_DUREE_CONTRAT}}'] = "Le bail est consenti pour une durée de 9 mois..."
        else:
             p['{{PARAGRAPHE_DUREE_CONTRAT}}'] = "Le bail est consenti pour une durée d'un an..."


        # --- Loyer et Charges ---
        financials = tenant.financials
        if financials:
            p['{{MONTANT_LOYER}}'] = f"{financials.loyer:.2f}"
            p['{{ASSAINISSEMENT}}'] = "Included" # ?? Needs granular check in financials/loyer DTO data
            # Financials object currently has aggregated charges, but DTO had granular.
            # We might need to map granular charges to financials entity or keep them in a dict in Tenant?
            # Assuming Financials entity holds them or we pass a separate Rent object? 
            # The user put granular charges in 'NotionLoyerDTO'.
            # Ideally Financials object should have these. I'll use placeholders for now or fix Financials entity.
            # Using defaults for safety if field missing in Number entity
            pass 
            
            p['{{MONTANT_CHARGES}}'] = f"{financials.charges:.2f}"
            p['{{MONTANT_TOTAL}}'] = f"{financials.loyer_CC:.2f}"
            # p['{{MONTANT_TOTAL_LETTRES}}'] = number_to_text(financials.loyer_CC) # Need util
            
        # --- Paiements Initiaux ---
        if financials:
            p['{{PRORATA_TOTAL_CC}}'] = f"{financials.prorata_total_CC:.2f}"
            p['{{TOTAL_1ER_MOIS}}'] = f"{financials.total_premier_mois:.2f}"
            p['{{MENTION_SPECIALE_LOYER}}'] = tenant.mention_speciale or ""

        # --- Signatures ---
        # {{DOC_VISA}} -> VISALE special text
        if tenant.type_garantie == GuarantorType.VISALE:
            p['{{DOC_VISA}}'] = f"Visa n° {tenant.numero_visale}..."
            p['{{SIGN_GARANT}}'] = "" # No signature for Visale usually
        else:
             p['{{DOC_VISA}}'] = ""
             p['{{SIGN_GARANT}}'] = "Signature du garant..."

        return p

    @staticmethod
    def _build_receipt_placeholders(tenant: Tenant, month: str, year: int) -> Dict[str, str]:
        p = {}
        # ... Similar logic for receipts ...
        p['{{MOIS_COURANT}}'] = month
        p['{{ANNEE_COURANTE}}'] = str(year)
        p['{{NOM_LOCATAIRE}}'] = tenant.full_name
        p['{{ADRESSE_LOGEMENT}}'] = tenant.property_obj.address if tenant.property_obj else ""
        
        fin = tenant.financials
        if fin:
             p['{{SOMME_DUE}}'] = f"{fin.loyer_CC:.2f}"
             p['{{MONTANT_LOYER}}'] = f"{fin.loyer:.2f}"
             p['{{MONTANT_CHARGES}}'] = f"{fin.charges:.2f}"
             
        # TODO: Logic for dates like "JOUR_DEBUT_QUITTANCE" (1st of month usually)
        return p

    @staticmethod
    def _build_requests_from_dict(placeholders: Dict[str, str]) -> List[Dict[str, Any]]:
        requests = []
        for key, value in placeholders.items():
            if value is None:
                value = "" # Safety
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': key,
                        'matchCase': True
                    },
                    'replaceText': str(value)
                }
            })
        return requests
