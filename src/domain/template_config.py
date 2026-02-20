from dataclasses import dataclass


@dataclass(frozen=True)
class LeaseTemplateConfig:
    """Configuration holding Google-specific template and folder IDs for lease generation."""
    bail_template_id: str
    caution_template_id: str
