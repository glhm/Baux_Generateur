from dataclasses import dataclass, field
from typing import List, Optional
from src.domain.entities.value_objects import Period
from src.domain.entities.room import Room
from src.domain.entities.property import Property
from src.domain.entities.financials import Numbers
from src.domain.entities.guarantor import Guarantor
from src.domain.enums import LeaseType, GuarantorType

@dataclass
class Tenant:
    """Represents a Tenant (Locataire) entity."""
    # From DTO fields
    nom: str
    envoyer_quittance: bool
    statut_envoi_quittance: Optional[str] = None
    activer_generation: bool = False
    email: Optional[str] = None
    type_bail: Optional[LeaseType] = None
    type_garantie: Optional[GuarantorType] = None
    numero_visale: Optional[str] = None
    numero_contrat_visale: Optional[str] = None
    date_emission_visale: Optional[str] = None
    date_naissance: Optional[str] = None
    lieu_naissance: Optional[str] = None
    jour_arrivee: Optional[int] = None
    mois_arrivee: Optional[str] = None
    annee_arrivee: Optional[int] = None
    date_fin: Optional[str] = None
    annees: List[str] = field(default_factory=list)
    mention_speciale: Optional[str] = None

    # Aggregates
    guarantors: List[Guarantor] = field(default_factory=list)
    property_obj: Optional[Property] = None
    room: Optional[Room] = None
    financials: Optional[Numbers] = None
    period: Optional[Period] = None
    
    @property
    def full_name(self) -> str:
        return self.nom 

    class Builder:
        def __init__(self):
            self._nom = ""
            self._envoyer_quittance = False
            self._statut_envoi_quittance = None
            self._activer_generation = False
            self._email = None
            self._type_bail = None
            self._type_garantie = None
            self._numero_visale = None
            self._numero_contrat_visale = None
            self._date_emission_visale = None
            self._date_naissance = None
            self._lieu_naissance = None
            self._jour_arrivee = None
            self._mois_arrivee = None
            self._annee_arrivee = None
            self._date_fin = None
            self._annees = []
            self._mention_speciale = None
            
            self._guarantors = []
            self._property_obj = None
            self._room = None
            self._financials = None
            self._period = None

        def with_nom(self, nom: str):
            self._nom = nom
            return self

        def with_envoyer_quittance(self, envo: bool):
            self._envoyer_quittance = envo
            return self

        def with_statut_envoi_quittance(self, statut: str):
            self._statut_envoi_quittance = statut
            return self

        def with_activer_generation(self, activer: bool):
            self._activer_generation = activer
            return self
            
        def with_email(self, email: str):
            self._email = email
            return self

        def with_type_bail(self, type_bail: str):
            # Conversion logic if string is passed
            if isinstance(type_bail, str):
                try:
                    self._type_bail = LeaseType(type_bail)
                except ValueError:
                    # Fallback or strict? Let's try to match by name or value casually
                    for t in LeaseType:
                        if t.value.lower() == type_bail.lower():
                            self._type_bail = t
                            break
            else:
                self._type_bail = type_bail
            return self

        def with_type_garantie(self, type_gar: str):
             if isinstance(type_gar, str):
                try:
                    self._type_garantie = GuarantorType(type_gar)
                except ValueError:
                    for t in GuarantorType:
                        if t.value.lower() == type_gar.lower():
                            self._type_garantie = t
                            break
             else:
                self._type_garantie = type_gar
             return self

        def with_visale_infos(self, numero: str, contrat: str, date_emission: str):
            self._numero_visale = numero
            self._numero_contrat_visale = contrat
            self._date_emission_visale = date_emission
            return self

        def with_naissance(self, date_n: str, lieu_n: str):
            self._date_naissance = date_n
            self._lieu_naissance = lieu_n
            return self

        def with_arrivee(self, jour: int, mois: str, annee: int):
            self._jour_arrivee = jour
            self._mois_arrivee = mois
            self._annee_arrivee = annee
            return self

        def with_date_fin(self, date_f: str):
            self._date_fin = date_f
            return self

        def with_annees(self, annees: List[str]):
            self._annees = annees
            return self
            
        def with_mention(self, mention: str):
            self._mention_speciale = mention
            return self

        def with_guarantors(self, guarantors: List[Guarantor]):
            self._guarantors = guarantors
            return self

        def with_property(self, prop: Property):
            self._property_obj = prop
            return self

        def with_room(self, room: Room):
            self._room = room
            return self

        def with_financials(self, numbers: Numbers):
            self._financials = numbers
            return self

        def with_period(self, period: Period):
            self._period = period
            return self

        def build(self) -> 'Tenant':
            if not self._nom:
                raise ValueError("Nom is required for Tenant")
            
            return Tenant(
                nom=self._nom,
                envoyer_quittance=self._envoyer_quittance,
                statut_envoi_quittance=self._statut_envoi_quittance,
                activer_generation=self._activer_generation,
                email=self._email,
                type_bail=self._type_bail,
                type_garantie=self._type_garantie,
                numero_visale=self._numero_visale,
                numero_contrat_visale=self._numero_contrat_visale,
                date_emission_visale=self._date_emission_visale,
                date_naissance=self._date_naissance,
                lieu_naissance=self._lieu_naissance,
                jour_arrivee=self._jour_arrivee,
                mois_arrivee=self._mois_arrivee,
                annee_arrivee=self._annee_arrivee,
                date_fin=self._date_fin,
                annees=self._annees,
                mention_speciale=self._mention_speciale,
                guarantors=self._guarantors,
                property_obj=self._property_obj,
                room=self._room,
                financials=self._financials,
                period=self._period
            )
