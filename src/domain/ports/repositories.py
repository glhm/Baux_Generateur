from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.tenant import Tenant
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.property import Property
# Assuming "Chambre" and "Loyer" might become entities or stay DTOs? 
# The user asked for Repositories for them, implying they are Domain Entities.
# I will define stub classes for Room/Rent if they aren't fully defined yet, or use generic dicts if the user hasn't defined entity structure (but they gave DTO structure).
# Ideally, Room and Rent should be Entities. I'll define simple classes for them if mostly just data holders.

class TenantRepository(ABC):
    @abstractmethod
    def get_all_tenants(self) -> List[Tenant]:
        pass

    @abstractmethod
    def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        pass

class GuarantorRepository(ABC):
    @abstractmethod
    def get_guarantor_by_name(self, name: str) -> Optional[Guarantor]:
        pass

class PropertyRepository(ABC):
    """Corresponds to 'Biens'"""
    @abstractmethod
    def get_property_by_name(self, name: str) -> Optional[Property]:
         pass

class RoomRepository(ABC):
    """Corresponds to 'Chambres'"""
    @abstractmethod
    def get_room_by_name(self, name: str) -> Optional['dict']: # Placeholder for Room Entity
        pass

class RentRepository(ABC):
    """Corresponds to 'Loyers'"""
    @abstractmethod
    def get_rent_by_name(self, name: str) -> Optional['dict']: # Placeholder for Rent Entity
        pass
