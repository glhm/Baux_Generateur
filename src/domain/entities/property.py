from dataclasses import dataclass
from typing import Optional

@dataclass
class Property:
    """Represents a Property (Bien) entity."""
    # Matched to NotionBienDTO
    address: str # "adresse" (Title)
    surface_habitable: Optional[str] = None
    numero_dpe: Optional[str] = None
    autres_parties: Optional[str] = None
    date_construction: Optional[int] = None
    designation: Optional[str] = None
    classe_dpe: Optional[str] = None
    elements_equipement: Optional[str] = None
    enumeration_contenu: Optional[str] = None
    modalite_chauffage: Optional[str] = None
    modalite_eau: Optional[str] = None
    nombre_pieces: Optional[int] = None
    regime_juridique: Optional[str] = None
    type_habitat: Optional[str] = None

    # Logic helpers
    @property
    def name(self) -> str:
        return self.address # Often address IS the name in this model

    class Builder:
        def __init__(self):
            self._address = ""
            self._surface_habitable = None
            self._numero_dpe = None
            self._autres_parties = None
            self._date_construction = None
            self._designation = None
            self._classe_dpe = None
            self._elements_equipement = None
            self._enumeration_contenu = None
            self._modalite_chauffage = None
            self._modalite_eau = None
            self._nombre_pieces = None
            self._regime_juridique = None
            self._type_habitat = None

        def with_adresse(self, adresse: str):
            self._address = adresse
            return self
        
        def with_surface_habitable(self, surf: str):
            self._surface_habitable = surf
            return self

        def with_dpe(self, numero: str, classe: str):
            self._numero_dpe = numero
            self._classe_dpe = classe
            return self

        def with_autres_parties(self, autres: str):
            self._autres_parties = autres
            return self

        def with_date_construction(self, date_constr: int):
            self._date_construction = date_constr
            return self

        def with_designation(self, des: str):
            self._designation = des
            return self

        def with_equipement(self, equip: str):
            self._elements_equipement = equip
            return self

        def with_enumeration(self, enu: str):
            self._enumeration_contenu = enu
            return self

        def with_modalites(self, chauffage: str, eau: str):
            self._modalite_chauffage = chauffage
            self._modalite_eau = eau
            return self
        
        def with_nombre_pieces(self, nb: int):
            self._nombre_pieces = nb
            return self
        
        def with_regime_juridique(self, regime: str):
            self._regime_juridique = regime
            return self

        def with_type_habitat(self, type_habit: str):
            self._type_habitat = type_habit
            return self

        def build(self) -> 'Property':
            if not self._address:
                raise ValueError("Address is required for Property")
            return Property(
                address=self._address,
                surface_habitable=self._surface_habitable,
                numero_dpe=self._numero_dpe,
                autres_parties=self._autres_parties,
                date_construction=self._date_construction,
                designation=self._designation,
                classe_dpe=self._classe_dpe,
                elements_equipement=self._elements_equipement,
                enumeration_contenu=self._enumeration_contenu,
                modalite_chauffage=self._modalite_chauffage,
                modalite_eau=self._modalite_eau,
                nombre_pieces=self._nombre_pieces,
                regime_juridique=self._regime_juridique,
                type_habitat=self._type_habitat
            )
