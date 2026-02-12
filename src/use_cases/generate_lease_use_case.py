from src.ports.template_renderer_port import TemplateRenderer
from src.domain.services.placeholder_service import PlaceholderService
from src.domain.entities.tenant import Tenant
from src.domain.entities.lease import Lease
from src.domain.entities.value_objects import Period
from src.conf.info_apis import ID_TEMPLATE_BAIL_MEUBLE, CAUTION_ID, ID_REPO_BAUX


class GenerateLeaseUseCase:

    def __init__(self, template_renderer: TemplateRenderer, placeholder_service: PlaceholderService):
        self.template_renderer = template_renderer
        self.placeholder_service = placeholder_service

    def execute(self, tenant: Tenant) -> None:
        """
        Generates and saves loan and guarantor documents for the given tenant.
        """
        # 1. Construct Lease entity
        lease = Lease(
            tenant=tenant,
            property=tenant.property_obj,
            period=Period(start_date=None),  # TODO: parse dates from Tenant if available
            rent=tenant.financials.rent,
            charges=tenant.financials.charges,
            deposit=tenant.financials.deposit
        )

        # 2. Compute Placeholders
        self.placeholder_service.compute(lease)
        replacements = self.placeholder_service.get()

        # 3. Render Lease Document
        doc_name = f"Bail_location_{tenant.full_name}"
        self.template_renderer.render(
            template_id=ID_TEMPLATE_BAIL_MEUBLE,
            placeholders=replacements,
            output_name=doc_name
        )

        # 4. Render Guarantor Document (if Physical)
        if tenant.type_garantie and tenant.type_garantie.value == "Physique":
            caution_name = f"Acte_de_caution_solidaire_{tenant.full_name}"
            self.template_renderer.render(
                template_id=CAUTION_ID,
                placeholders=replacements,
                output_name=caution_name
            )
