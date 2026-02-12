from abc import ABC, abstractmethod


from typing import List


from src.domain.entities.tenant import Tenant


class LeaseRepository(ABC):


    @abstractmethod
    def get_all_concerned_leases(self) -> List[Tenant]:

        """Retrieves a list of leases."""
        pass


