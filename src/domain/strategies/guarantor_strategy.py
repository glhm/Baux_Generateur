from abc import ABC, abstractmethod
from src.domain.entities.guarantor import Guarantor

class GuarantorStrategy(ABC):
    @abstractmethod
    def validate(self, guarantor: Guarantor) -> bool:
        pass

class PhysicalGuarantorStrategy(GuarantorStrategy):
    def validate(self, guarantor: Guarantor) -> bool:
        # Physical guarantor might need address, etc.
        return True

class VisaleGuarantorStrategy(GuarantorStrategy):
    def validate(self, guarantor: Guarantor) -> bool:
         # Visale might need specific ID format?
        return True

class GuarantorStrategyFactory:
    @staticmethod
    def get_strategy(type_caution: str) -> GuarantorStrategy:
        if type_caution == "Physique":
            return PhysicalGuarantorStrategy()
        elif type_caution == "Visale":
            return VisaleGuarantorStrategy()
        else:
            # Default or error
            return PhysicalGuarantorStrategy()
