from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Room:
    """Represents a Room (Chambre) entity."""
    name: str # nom
    localisation: Optional[str] = None
    surface: Optional[float] = None
    volume: Optional[str] = None # Or float? DTO said str (Texte/Unité)
    # linked IDs might not be needed in Domain Entity if we use object references, 
    # but for now let's keep them or just rely on aggregation in Tenant?
    # Tenant has a Room. Room might belong to a Property. 
    # In Clean Architecture, Entities should ideally link by Reference or ID. 
    # Let's keep data fields.

    class Builder:
        def __init__(self):
            self._name = ""
            self._localisation = None
            self._surface = None
            self._volume = None

        def with_name(self, name: str):
            self._name = name
            return self

        def with_localisation(self, loc: str):
            self._localisation = loc
            return self
        
        def with_surface(self, surf: float):
            self._surface = surf
            return self

        def with_volume(self, vol: str):
            self._volume = vol
            return self

        def build(self) -> 'Room':
            if not self._name:
                raise ValueError("Room name is required")
            return Room(
                name=self._name,
                localisation=self._localisation,
                surface=self._surface,
                volume=self._volume
            )
