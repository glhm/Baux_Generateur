from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Tenant:
    """Represents a Tenant (Locataire) entity - Personal Information Only."""
    # Required fields – always filled in Notion
    nom: str
    email: str
    date_naissance: str
    lieu_naissance: str
    
    # Lease Configuration specific to this tenant's request/file?
    # Or should these be on the Lease? 
    # The user said "Tenant represents the real person".
    # But checks like "EnvoyerQuittance" are about the *relationship* (Lease).
    # However, Notion stores them on the Tenant page. 
    # Let's keep them here for now as they are attributes of the "Tenant entry" in Notion.
    envoyer_quittance: bool
    activer_generation: bool
    activer_generation_quittances: bool
    statut_envoi_quittance: str
    years: List[str] # List of years to generate receipts for
    


    # Dates - arrival/departure moved to Lease
    # annees stays as needed for receipt generation config? 
    # User said "years" (List[str]). But we also have "annees" (List[str]). Duplicate?
    # "years" in line 24. "annees" in line 38.
    # Tenant mapper maps "ANNEES" to "years" in line 51.
    # And maps "ANNEES" to "annees" in line 61?
    # I should check if I need to keep "annees". Line 38 has `annees: List[str]`.
    # Line 24 `years: List[str]`.
    # Step 471 added `years`.
    # Tenant had `annees` before?
    # I will remove the duplicate `annees` if `years` is enough. 
    # But `tenant_mapper` uses `annees` logic.
    # I'll keep `years` (new) and remove `annees` (old/duplicate) if possible.
    # But for now I'll just remove the fields requested.
    
    # Optional
    # mention_speciale moved to Lease 

    @property
    def full_name(self) -> str:
        return self.nom 

    class Builder:
        def __init__(self):
            self._nom = ""
            self._email = ""
            self._date_naissance = ""
            self._lieu_naissance = ""
            self._envoyer_quittance = False
            self._activer_generation = False
            self._activer_generation_quittances = False
            self._statut_envoi_quittance = ""
            self._years = []



        def with_nom(self, nom: str):
            self._nom = nom
            return self

        def with_email(self, email: str):
            self._email = email
            return self

        def with_naissance(self, date_n: str, lieu_n: str):
            self._date_naissance = date_n
            self._lieu_naissance = lieu_n
            return self

        def with_envoyer_quittance(self, envo: bool):
            self._envoyer_quittance = envo
            return self

        def with_activer_generation(self, active: bool):
            self._activer_generation = active
            return self

        def with_activer_generation_quittances(self, active: bool):
            self._activer_generation_quittances = active
            return self

        def with_statut_envoi_quittance(self, statut: str):
            self._statut_envoi_quittance = statut
            return self

        def with_years(self, years: List[str]):
            self._years = years
            return self







        def build(self) -> 'Tenant':
            if not self._nom:
                raise ValueError("Nom is required for Tenant")
            
            return Tenant(
                nom=self._nom,
                email=self._email,
                date_naissance=self._date_naissance,
                lieu_naissance=self._lieu_naissance,
                envoyer_quittance=self._envoyer_quittance,
                activer_generation=self._activer_generation,
                activer_generation_quittances=self._activer_generation_quittances,
                statut_envoi_quittance=self._statut_envoi_quittance,
                years=self._years,
            )
