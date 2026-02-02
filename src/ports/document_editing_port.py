# application/ports/document_editing_port.py
from abc import ABC, abstractmethod
from typing import Dict

class DocumentEditingPort(ABC):
    @abstractmethod
    def update_placeholders(self, document_id: str, replacements: Dict[str, str]):
        """Met à jour les placeholders dans le document"""
        pass
