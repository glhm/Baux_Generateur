from typing import Optional
from src.domain.ports.repositories import GuarantorRepository
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.value_objects import Address

class NotionGuarantorRepository(GuarantorRepository):
    def __init__(self, database_id: str):
        self.database_id = database_id

    def get_guarantor_by_name(self, name: str) -> Optional[Guarantor]:
        # TODO: Implement Notion fetch
        return Guarantor(
            first_name="Pascal",
            last_name="Sourdeau",
            address=Address("9 Rue Du Verger", "Longue-Jumelles", "53200"),
            email="pascalsourdeau@orange.fr",
            phone_number="0680085099",
            type_caution="Physique"
        )
