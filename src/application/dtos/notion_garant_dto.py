from dataclasses import dataclass
from typing import Optional

@dataclass
class NotionGarantDTO:
    """DTO representing a Guarantor (Garant) in Notion."""
    page_id: str
    nom_complet: str
    email: Optional[str] = None
    masquer: bool = False
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    date_naissance: Optional[str] = None
    lieu_naissance: Optional[str] = None

    class Builder:
        def __init__(self):
            self._page_id = ""
            self._nom_complet = ""
            self._email = None
            self._masquer = False
            self._telephone = None
            self._adresse = None
            self._date_naissance = None
            self._lieu_naissance = None

        def with_page_id(self, page_id: str):
            self._page_id = page_id
            return self

        def with_nom_complet(self, nom: str):
            self._nom_complet = nom
            return self

        def with_email(self, email: str):
            self._email = email
            return self
        
        def with_masquer(self, masquer: bool):
            self._masquer = masquer
            return self

        def with_telephone(self, tel: str):
            self._telephone = tel
            return self

        def with_adresse(self, adresse: str):
            self._adresse = adresse
            return self

        def with_date_naissance(self, date_naissance: str):
            self._date_naissance = date_naissance
            return self
            
        def with_lieu_naissance(self, lieu: str):
            self._lieu_naissance = lieu
            return self

        def build(self) -> 'NotionGarantDTO':
            if not self._page_id or not self._nom_complet:
                raise ValueError("Page ID and Nom Complet are required")
                
            return NotionGarantDTO(
                page_id=self._page_id,
                nom_complet=self._nom_complet,
                email=self._email,
                masquer=self._masquer,
                telephone=self._telephone,
                adresse=self._adresse,
                date_naissance=self._date_naissance,
                lieu_naissance=self._lieu_naissance
            )
