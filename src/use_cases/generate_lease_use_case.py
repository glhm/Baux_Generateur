from src.ports.template_renderer_port import TemplateRenderer
from src.domain.services.placeholder_service import PlaceholderService
from src.domain.entities.lease import Lease
from src.conf.info_apis import ID_TEMPLATE_BAIL_MEUBLE, CAUTION_ID

class GenerateLeaseUseCase:

    def __init__(self, template_renderer: TemplateRenderer, placeholder_service: PlaceholderService):
        self.template_renderer = template_renderer
        self.placeholder_service = placeholder_service

    def execute(self, lease: Lease) -> None:
        """
        Generates and save loan and guarantor documents for the given lease.
        Expected input is a fully constructed Lease aggregate.
        """
        tenant = lease.tenant
        
        # 1. Compute Placeholders using the Lease aggregate
        replacements = self.placeholder_service.generate_placeholders(lease)

        # 2. Render Lease Document
        doc_name = f"Bail_location_{tenant.full_name}"
        self.template_renderer.render(
            template_id=ID_TEMPLATE_BAIL_MEUBLE,
            placeholders=replacements,
            output_name=doc_name
        )

        # 3. Render Guarantor Document (if Physical)
        # Check tenant type_garantie OR check existence of PhysicalGuarantors in list
        if lease.is_physical_guarantor():
            caution_name = f"Acte_de_caution_solidaire_{tenant.full_name}"
            self.template_renderer.render(
                template_id=CAUTION_ID,
                placeholders=replacements,
                output_name=caution_name
            )
