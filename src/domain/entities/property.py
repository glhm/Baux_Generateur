from dataclasses import dataclass

@dataclass
class Property:
    """Represents a Property (Bien) entity."""
    id: str # Notion Page ID
    # Removed city, postal_code
    address: str
    owner_name: str
    owner_address: str
    surface_habitable: str
    numero_dpe: str
    autres_parties: str
    date_construction: int
    designation: str
    classe_dpe: str
    elements_equipement: str
    enumeration_contenu: str
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
            self._owner_name = ""
            self._owner_address = ""
            self._surface_habitable = ""
            self._numero_dpe = ""
            self._autres_parties = ""
            self._date_construction = 0
            self._designation = ""
            self._classe_dpe = ""
            self._elements_equipement = ""
            self._enumeration_contenu = ""
            self._modalite_chauffage = ""
            self._modalite_eau = ""
            self._nombre_pieces = 0
            self._regime_juridique = ""
            self._type_habitat = ""

        def with_id(self, id: str):
            self._id = id
            return self

        def with_adresse(self, adresse: str):
            self._address = adresse
            return self
            
        def with_owner_name(self, name: str):
            self._owner_name = name
            return self

        def with_owner_address(self, addr: str):
            self._owner_address = addr
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
                id=self._id,
                address=self._address,
                owner_name=self._owner_name,
                owner_address=self._owner_address,
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
