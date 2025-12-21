from typing import Optional
from src.domain.ports.repositories import PropertyRepository
from src.domain.entities.property import Property
from src.domain.entities.value_objects import Address

class NotionPropertyRepository(PropertyRepository):
    def __init__(self, database_id: str):
        self.database_id = database_id
        # In a real impl, inject requests/api_client or inherit from base NotionAdapter

    def get_property_by_name(self, name: str) -> Optional[Property]:
        # TODO: Implement actual Notion fetch
        # For now, return a placeholder to allow flow test
        return Property(
            name=name,
            address=Address("123 Rue Fake", "Paris", "75000"),
            furniture_type="Meublé",
            details="Great apartment",
            owner_name="Me"
        )
