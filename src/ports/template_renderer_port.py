from abc import ABC, abstractmethod
from typing import Dict


class TemplateRenderer(ABC):

    @abstractmethod
    def render(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        output_name: str,
        folder_id: str = None
    ) -> str:
        """
        Renders a document from a template by replacing placeholders,
        and returns the ID or path of the generated document.
        """
        pass
