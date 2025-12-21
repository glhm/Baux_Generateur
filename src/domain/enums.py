from enum import Enum

class LeaseType(Enum):
    MEUBLE = "Meublé"
    ETUDIANT = "Etudiant"
    NU = "Nu"

class GuarantorType(Enum):
    PHYSIQUE = "Physique"
    VISALE = "Visale"
