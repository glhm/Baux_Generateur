from dataclasses import dataclass

@dataclass
class Property:
    """Represents a Property (Bien) entity."""
    id: str # Notion Page ID
    # Removed city, postal_code
    address: str
    surface_habitable: str
    autres_parties: str
    date_construction: int
    designation: str
    classe_dpe: str
    elements_equipement_logement: str
    enumeration_communs: str
    modalite_chauffage: str
    modalite_eau: str
    nombre_pieces: int
    regime_juridique: str
    type_habitat: str

    @property
    def name(self) -> str:
        return self.address

    class Builder:
        def __init__(self):
            self._id = ""
            self._address = ""
            self._surface_habitable = ""
            self._autres_parties = ""
            self._date_construction = 0
            self._designation = ""
            self._classe_dpe = ""
            self._elements_equipement_logement = ""
            self._enumeration_communs = ""
            self._modalite_chauffage = ""
            self._modalite_eau = ""
            self._nombre_pieces = 0
            self._regime_juridique = ""
            self._type_habitat = ""

        def with_id(self, id: str):
            self._id = id
            return self

        def with_address(self, adresse: str):
            self._address = adresse
            return self
                    
        def with_surface_habitable(self, surf: str):
            self._surface_habitable = surf
            return self

        def with_dpe(self, classe: str):
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

        def with_elements_equipement_logement(self, equip: str):
            self._elements_equipement_logement = equip
            return self

        def with_enumeration_communs(self, enu: str):
            self._enumeration_communs = enu
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
                id=self._id,
                address=self._address,
                surface_habitable=self._surface_habitable,
                autres_parties=self._autres_parties,
                date_construction=self._date_construction,
                designation=self._designation,
                classe_dpe=self._classe_dpe,
                elements_equipement_logement=self._elements_equipement_logement,
                enumeration_communs=self._enumeration_communs,
                modalite_chauffage=self._modalite_chauffage,
                modalite_eau=self._modalite_eau,
                nombre_pieces=self._nombre_pieces,
                regime_juridique=self._regime_juridique,
                type_habitat=self._type_habitat
            )
