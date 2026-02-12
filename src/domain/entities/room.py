from dataclasses import dataclass

@dataclass
class Room:
    """Represents a Room (Chambre) entity."""
    # All fields are always filled in Notion DB
    name: str
    localisation: str
    surface: float
    volume: str

    class Builder:
        def __init__(self):
            self._name = ""
            self._localisation = ""
            self._surface = 0.0
            self._volume = ""

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
