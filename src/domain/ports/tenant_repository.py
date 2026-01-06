from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.tenant import Tenant

class TenantRepository(ABC):
    @abstractmethod
    def get_tenants(self) -> List[Tenant]:
        """Retrieves a list of tenants."""
        pass
