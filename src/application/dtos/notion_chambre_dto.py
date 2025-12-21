from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NotionChambreDTO:
    """DTO representing a Room (Chambre) in Notion."""
    page_id: str
    nom: str
    localisation: Optional[str] = None
    surface: Optional[float] = None
    volume: Optional[str] = None
    biens_ids: List[str] = field(default_factory=list)
    locataires_ids: List[str] = field(default_factory=list)

    class Builder:
        def __init__(self):
            self._page_id = ""
            self._nom = ""
            self._localisation = None
            self._surface = None
            self._volume = None
            self._biens_ids = []
            self._locataires_ids = []

        def with_page_id(self, page_id: str):
            self._page_id = page_id
            return self

        def with_nom(self, nom: str):
            self._nom = nom
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

        def with_biens_ids(self, ids: List[str]):
            self._biens_ids = ids
            return self

        def with_locataires_ids(self, ids: List[str]):
            self._locataires_ids = ids
            return self

        def build(self) -> 'NotionChambreDTO':
            if not self._page_id or not self._nom:
                raise ValueError("Page ID and Nom are required")

            return NotionChambreDTO(
                page_id=self._page_id,
                nom=self._nom,
                localisation=self._localisation,
                surface=self._surface,
                volume=self._volume,
                biens_ids=self._biens_ids,
                locataires_ids=self._locataires_ids
            )
