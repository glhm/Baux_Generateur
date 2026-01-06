from dataclasses import dataclass
from typing import Optional
from src.domain.enums import GuarantorType

@dataclass
class Guarantor:
    """Represents a Guarantor (Garant) entity."""
    # Matched to NotionGarantDTO
    full_name_raw: str 
    email: Optional[str] = None
    masquer: bool = False
    phone_number: Optional[str] = None
    address_raw: Optional[str] = None
    date_naissance: Optional[str] = None
    lieu_naissance: Optional[str] = None
    type_caution: Optional[GuarantorType] = None # Added field if relevant for Guarantor entity itself, though Tenant has 'type_garantie'
    
    @property
    def full_name(self) -> str:
        return self.full_name_raw

    class Builder:
        def __init__(self):
            self._full_name_raw = ""
            self._email = None
            self._masquer = False
            self._phone_number = None
            self._address_raw = None
            self._date_naissance = None
            self._lieu_naissance = None
            self._type_caution = None

        def with_nom_complet(self, nom: str):
            self._full_name_raw = nom
            return self

        def with_email(self, email: str):
            self._email = email
            return self
        
        def with_masquer(self, masquer: bool):
            self._masquer = masquer
            return self

        def with_telephone(self, tel: str):
            self._phone_number = tel
            return self

        def with_adresse(self, adresse: str):
            self._address_raw = adresse
            return self

        def with_date_naissance(self, date: str):
            self._date_naissance = date
            return self

        def with_lieu_naissance(self, lieu: str):
            self._lieu_naissance = lieu
            return self
            
        def with_type_caution(self, type_c: str):
             if isinstance(type_c, str):
                try:
                    self._type_caution = GuarantorType(type_c)
                except ValueError:
                    pass
             else:
                self._type_caution = type_c
             return self

        def build(self) -> 'Guarantor':
            if not self._full_name_raw:
                raise ValueError("Guarantor name is required")
            return Guarantor(
                full_name_raw=self._full_name_raw,
                email=self._email,
                masquer=self._masquer,
                phone_number=self._phone_number,
                address_raw=self._address_raw,
                date_naissance=self._date_naissance,
                lieu_naissance=self._lieu_naissance,
                type_caution=self._type_caution
            )
