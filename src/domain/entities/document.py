from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Document:
    name: str
    template_id: str
    replacements: Dict[str, str] = field(default_factory=dict)
    output_path: str = ""

    class Builder:
        def __init__(self, template_id: str):
            self._document = Document(name="", template_id=template_id)
        
        def with_name(self, name: str) -> 'Document.Builder':
            self._document.name = name
            return self

        def add_replacement(self, key: str, value: Any) -> 'Document.Builder':
            self._document.replacements[key] = str(value)
            return self

        def with_replacements(self, replacements: Dict[str, Any]) -> 'Document.Builder':
            for k, v in replacements.items():
                self.add_replacement(k, v)
            return self

        def build(self) -> 'Document':
            if not self._document.name:
                raise ValueError("Document name is required")
            return self._document
