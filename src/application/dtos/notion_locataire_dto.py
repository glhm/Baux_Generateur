from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NotionLocataireDTO:
    """DTO representing a Tenant (Locataire) in Notion."""
    page_id: str
    nom: str
    envoyer_quittance: bool
    statut_envoi_quittance: Optional[str] = None
    activer_generation: bool = False
    email: Optional[str] = None
    type_bail: Optional[str] = None
    type_garantie: Optional[str] = None
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

    class Builder:
        def __init__(self):
            # Using placeholders/defaults for required fields initially or requiring them in constructor?
            # User wants a Builder mechanism.
            self._page_id = ""
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

        def with_page_id(self, page_id: str):
            self._page_id = page_id
            return self

        def with_nom(self, nom: str):
            self._nom = nom
            return self

        def with_envoyer_quittance(self, envoyer: bool):
            self._envoyer_quittance = envoyer
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
            self._type_bail = type_bail
            return self

        def with_type_garantie(self, type_garantie: str):
            self._type_garantie = type_garantie
            return self

        def with_numero_visale(self, numero: str):
            self._numero_visale = numero
            return self

        def with_numero_contrat_visale(self, numero: str):
            self._numero_contrat_visale = numero
            return self

        def with_date_emission_visale(self, date_emission: str):
            self._date_emission_visale = date_emission
            return self

        def with_date_naissance(self, date_naissance: str):
            self._date_naissance = date_naissance
            return self

        def with_lieu_naissance(self, lieu: str):
            self._lieu_naissance = lieu
            return self

        def with_jour_arrivee(self, jour: int):
            self._jour_arrivee = jour
            return self

        def with_mois_arrivee(self, mois: str):
            self._mois_arrivee = mois
            return self

        def with_annee_arrivee(self, annee: int):
            self._annee_arrivee = annee
            return self
            
        def with_date_fin(self, date_fin: str):
            self._date_fin = date_fin
            return self

        def with_annees(self, annees: List[str]):
            self._annees = annees
            return self
            
        def with_mention_speciale(self, mention: str):
            self._mention_speciale = mention
            return self

        def build(self) -> 'NotionLocataireDTO':
            # Basic validation
            if not self._page_id:
                raise ValueError("Page ID is required")
            if not self._nom:
                raise ValueError("Nom is required")
                
            return NotionLocataireDTO(
                page_id=self._page_id,
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
                mention_speciale=self._mention_speciale
            )
