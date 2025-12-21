from dataclasses import dataclass, field
from typing import Optional

@dataclass
class NotionLoyerDTO:
    """DTO representing Rent/Charges (Loyer) in Notion."""
    page_id: str
    nom: str
    montant_loyer: Optional[float] = None
    montant_charges: Optional[float] = None
    montant_total_texte: Optional[str] = None
    assainissement: Optional[float] = None
    eau: Optional[float] = None
    electricite: Optional[float] = None
    wifi: Optional[float] = None
    menage: Optional[float] = None
    chauffage: Optional[float] = None

    class Builder:
        def __init__(self):
            self._page_id = ""
            self._nom = ""
            self._montant_loyer = None
            self._montant_charges = None
            self._montant_total_texte = None
            self._assainissement = None
            self._eau = None
            self._electricite = None
            self._wifi = None
            self._menage = None
            self._chauffage = None

        def with_page_id(self, page_id: str):
            self._page_id = page_id
            return self

        def with_nom(self, nom: str):
            self._nom = nom
            return self

        def with_montant_loyer(self, montant: float):
            self._montant_loyer = montant
            return self
        
        def with_montant_charges(self, montant: float):
            self._montant_charges = montant
            return self

        def with_montant_total_texte(self, texte: str):
            self._montant_total_texte = texte
            return self

        def with_assainissement(self, montant: float):
            self._assainissement = montant
            return self

        def with_eau(self, montant: float):
            self._eau = montant
            return self

        def with_electricite(self, montant: float):
            self._electricite = montant
            return self
            
        def with_wifi(self, montant: float):
            self._wifi = montant
            return self

        def with_menage(self, montant: float):
            self._menage = montant
            return self
            
        def with_chauffage(self, montant: float):
            self._chauffage = montant
            return self

        def build(self) -> 'NotionLoyerDTO':
            if not self._page_id or not self._nom:
                 # Note: in real Notion, title might be empty but ID always exists.
                 # Enforcing name here for safety.
                 raise ValueError("Page ID and Nom are required")

            return NotionLoyerDTO(
                page_id=self._page_id,
                nom=self._nom,
                montant_loyer=self._montant_loyer,
                montant_charges=self._montant_charges,
                montant_total_texte=self._montant_total_texte,
                assainissement=self._assainissement,
                eau=self._eau,
                electricite=self._electricite,
                wifi=self._wifi,
                menage=self._menage,
                chauffage=self._chauffage
            )
