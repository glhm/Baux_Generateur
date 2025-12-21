from typing import Optional
from src.domain.ports.repositories import RoomRepository, RentRepository

class NotionRoomRepository(RoomRepository):
    def __init__(self, database_id: str):
        self.database_id = database_id

    def get_room_by_name(self, name: str) -> Optional[dict]:
        # TODO: Implement Notion fetch
        return {"name": name, "surface": 12.0}

class NotionRentRepository(RentRepository):
    def __init__(self, database_id: str):
        self.database_id = database_id

    def get_rent_by_name(self, name: str) -> Optional[dict]:
        # TODO: Implement Notion fetch
        # Return dict matching what GenerateLeaseUseCase expects
        return {"loyer": 500.0, "charges": 50.0, "name": name}
