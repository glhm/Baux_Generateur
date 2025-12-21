from abc import ABC, abstractmethod
from src.domain.entities.lease import Lease
from src.domain.entities.value_objects import Period

class LeaseGenerationStrategy(ABC):
    @abstractmethod
    def customize_lease(self, lease_builder: 'Lease.Builder') -> None:
        """Applies specific rules to the lease builder."""
        pass

class FurnishedLeaseStrategy(LeaseGenerationStrategy):
    def customize_lease(self, lease_builder: 'Lease.Builder') -> None:
        # Example logic: Furnished leases might have specific clauses or duration defaults
        # For now, we'll just log or set a flag if we had one.
        # In a real app, this would add specific clauses to the document replacements.
        pass

class UnfurnishedLeaseStrategy(LeaseGenerationStrategy):
    def customize_lease(self, lease_builder: 'Lease.Builder') -> None:
        pass

class StudentLeaseStrategy(LeaseGenerationStrategy):
    def customize_lease(self, lease_builder: 'Lease.Builder') -> None:
        # Student lease often 9 months
        pass

class LeaseStrategyFactory:
    @staticmethod
    def get_strategy(lease_type: str) -> LeaseGenerationStrategy:
        if lease_type == "Meublé":
            return FurnishedLeaseStrategy()
        elif lease_type == "Non-meublé":
            return UnfurnishedLeaseStrategy()
        elif lease_type == "Etudiant":
            return StudentLeaseStrategy()
        else:
            raise ValueError(f"Unknown lease type: {lease_type}")
