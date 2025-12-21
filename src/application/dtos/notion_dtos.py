from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NotionLocataireDTO:
    """DTO representing a Tenant (Locataire) in Notion."""
    page_id: str
    nom: str  # Titre (Name)
    envoyer_quittance: bool  # EnvoyerQuittance
    statut_envoi_quittance: Optional[str] = None  # EnvoiQuittanceRe...
    activer_generation: bool = False  # ActiverGeneration
    email: Optional[str] = None  # Mail
    type_bail: Optional[str] = None  # TypeDeBail (Meuble, etc.)
    type_garantie: Optional[str] = None  # Garantie (Visale, etc.)
    numero_visale: Optional[str] = None  # {N_VISALE}
    numero_contrat_visale: Optional[str] = None  # {N_CONTRAT_VIS...}
    date_emission_visale: Optional[str] = None  # {DATE_EMISSION_...}
    date_naissance: Optional[str] = None  # {DATE_NAISSANC...}
    lieu_naissance: Optional[str] = None  # {LIEU_NAISSANCE...}
    jour_arrivee: Optional[int] = None  # {JOUR_ARRIVEE}
    mois_arrivee: Optional[str] = None  # {MOIS_ARRIVEE}
    annee_arrivee: Optional[int] = None  # {ANNEE_ARRIVEE}
    date_fin: Optional[str] = None  # {DATE_FIN}
    annees: List[str] = field(default_factory=list)  # ANNEES (Multi-select)
    mention_speciale: Optional[str] = None  # MENTION_SPECIA...

@dataclass
class NotionGarantDTO:
    """DTO representing a Guarantor (Garant) in Notion."""
    page_id: str
    nom_complet: str  # Pascal, Léon Sourdeau
    email: Optional[str] = None  # E-mail
    masquer: bool = False  # Masquer
    telephone: Optional[str] = None  # Téléphone
    adresse: Optional[str] = None  # {ADRESSE_GARAN...}
    date_naissance: Optional[str] = None  # {DATE_NAISSANC...}
    lieu_naissance: Optional[str] = None  # {LIEU_NAISSANCE...}

@dataclass
class NotionChambreDTO:
    """DTO representing a Room (Chambre) in Notion."""
    page_id: str
    nom: str  # 1 Auduc
    localisation: Optional[str] = None  # {LOCALISATION}
    surface: Optional[float] = None  # {SURFACE_CHAM...}
    volume: Optional[str] = None  # {VOLUME_HABITA...} (Texte/Unité ?)
    biens_ids: List[str] = field(default_factory=list)  # Relation Biens
    locataires_ids: List[str] = field(default_factory=list)  # Relation Locataires

@dataclass
class NotionLoyerDTO:
    """DTO representing Rent/Charges (Loyer) in Notion."""
    page_id: str
    nom: str  # 320 Richet
    montant_loyer: Optional[float] = None  # {MONTANT_LOYER}
    montant_charges: Optional[float] = None  # {MONTANT_CHAR...}
    montant_total_texte: Optional[str] = None  # {MONTANT_TOTA...}
    assainissement: Optional[float] = None  # {ASSAINISSEMENT}
    eau: Optional[float] = None  # {EAU}
    electricite: Optional[float] = None  # {ELEC}
    wifi: Optional[float] = None  # {WIFI}
    menage: Optional[float] = None  # {MENAGE}
    chauffage: Optional[float] = None  # {CHAUFFAGE}

@dataclass
class NotionBienDTO:
    """DTO representing a Property (Bien) in Notion."""
    page_id: str
    adresse: str  # Titre
    surface_habitable: Optional[str] = None  # {SURFACE_HABITA...}
    numero_dpe: Optional[str] = None  # Numéro DPE
    autres_parties: Optional[str] = None  # {AUTRES_PARTIES_...}
    date_construction: Optional[int] = None  # {DATE_CONSTRU...}
    designation: Optional[str] = None  # {DESIGNATION_BI...}
    classe_dpe: Optional[str] = None  # {DPE}
    elements_equipement: Optional[str] = None  # {ELEMENTS_EQUIP...}
    enumeration_contenu: Optional[str] = None  # {ENUMERATION_C...} (Texte Long)
    modalite_chauffage: Optional[str] = None  # {MODALITE_CHAU...}
    modalite_eau: Optional[str] = None  # {MODALITE_EAU}
    nombre_pieces: Optional[int] = None  # {NOMBRE_PIECES}
    regime_juridique: Optional[str] = None  # {REGIME_JURIDIQ...}
    type_habitat: Optional[str] = None  # {TYPE_HABITAT}
    locataires_ids: List[str] = field(default_factory=list)  # Relation Locataires
    chambres_ids: List[str] = field(default_factory=list)  # Relation Chambres
