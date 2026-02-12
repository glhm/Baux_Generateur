from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional

@dataclass
class Guarantor(ABC):
    """Abstract base class for a Guarantor."""
    # Common fields? Maybe just name/email?
    # Or maybe nothing common if structure differs wildly?
    # Let's assume Name is common.
    pass

@dataclass
class PhysicalGuarantor(Guarantor):
    """Represents a physical person Guarantor."""
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

@dataclass
class VisaleGuarantor(Guarantor):
    """Represents a Visale Guarantor (Agency/State)."""
    numero_visale: Optional[str]
    numero_contrat_visale: Optional[str]
    date_emission_visale: Optional[str]
    # Visale doesn't have address/birthdate of a person usually, 
    # but strictly speaking `GuarantorType.VISALE` was used on Tenant.
