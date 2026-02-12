from dataclasses import dataclass

@dataclass
class Guarantor:
    """Represents a Guarantor (Garant) entity."""
    # All fields are always filled in Notion DB
    full_name_raw: str
    email: str
    phone_number: str
    address_raw: str
    date_naissance: str
    lieu_naissance: str
    masquer: bool = False

    @property
    def full_name(self) -> str:
        return self.full_name_raw

    class Builder:
        def __init__(self):
            self._full_name_raw = ""
            self._email = ""
            self._masquer = False
            self._phone_number = ""
            self._address_raw = ""
            self._date_naissance = ""
            self._lieu_naissance = ""

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
            )
