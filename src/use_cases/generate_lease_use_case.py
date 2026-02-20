from src.ports.template_renderer_port import TemplateRenderer
from src.domain.services.placeholder_service import PlaceholderService
from src.domain.services.financials_service import FinancialsService
from src.domain.entities.lease import Lease
from src.domain.template_config import LeaseTemplateConfig


class GenerateLeaseUseCase:

    def __init__(self, template_renderer: TemplateRenderer, placeholder_service: PlaceholderService, template_config: LeaseTemplateConfig):
        self.template_renderer = template_renderer
        self.placeholder_service = placeholder_service
        self.template_config = template_config

    def execute(self, lease: Lease) -> None:
        """
        Generates and save loan and guarantor documents for the given lease.
        Expected input is a fully constructed Lease aggregate.
        """
        tenant = lease.tenant

        # 1. Compute Financials (domain service)
        lease.financials = FinancialsService.compute_prorata(lease)
        
        # 2. Compute Placeholders using the Lease aggregate
        replacements = self.placeholder_service.generate_placeholders(lease)

        # 3. Render Lease Document
        doc_name = f"Bail_location_{tenant.full_name}"
        self.template_renderer.render(
            template_id=self.template_config.bail_template_id,
            placeholders=replacements,
            output_name=doc_name
        )

        # 4. Render Guarantor Document (if Physical)
        if lease.is_physical_guarantor():
            caution_name = f"Acte_de_caution_solidaire_{tenant.full_name}"
            self.template_renderer.render(
                template_id=self.template_config.caution_template_id,
                placeholders=replacements,
                output_name=caution_name
            )

