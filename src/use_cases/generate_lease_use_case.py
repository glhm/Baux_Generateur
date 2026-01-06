from src.domain.ports.document_repository import DocumentRepository
from src.domain.services.placeholder_service import PlaceholderService
from src.domain.entities.tenant import Tenant
from src.domain.entities.lease import Lease
from src.domain.entities.document import Document
from src.domain.entities.value_objects import Period
from src.conf.info_apis import ID_TEMPLATE_BAIL_MEUBLE, CAUTION_ID, ID_REPO_BAUX

class GenerateLeaseUseCase:
    def __init__(self, document_repository: DocumentRepository, placeholder_service: PlaceholderService):
        self.document_repository = document_repository
        self.placeholder_service = placeholder_service

    def execute(self, tenant: Tenant) -> None:
        """
        Generates and saves loan and guarantor documents for the given tenant.
        """
        # 1. Construct Lease entity
        # Assuming we create a Lease snapshot from the current Tenant state.
        # Note: Tenant entity currently holds property, financials etc as aggregates.
        lease = Lease(
            tenant=tenant,
            property=tenant.property_obj,
            period=Period(start_date=None), # TODO: parse dates from Tenant if available
            rent=tenant.financials.rent,
            charges=tenant.financials.charges,
            deposit=tenant.financials.deposit
        )

        # 2. Generate Placeholders
        replacements = self.placeholder_service.generate_placeholders(lease)

        # 3. Create & Save Lease Document
        doc_name = f"Bail_location_{tenant.full_name}"
        lease_doc = Document.Builder(ID_TEMPLATE_BAIL_MEUBLE)\
            .with_name(doc_name)\
            .with_replacements(replacements)\
            .build()
        
        self.document_repository.save_document(lease_doc, ID_REPO_BAUX)

        # 4. Create & Save Guarantor Document (if Physical)
        if tenant.type_garantie and tenant.type_garantie.value == "Physique":
            caution_name = f"Acte_de_caution_solidaire_{tenant.full_name}"
            caution_doc = Document.Builder(CAUTION_ID)\
                .with_name(caution_name)\
                .with_replacements(replacements)\
                .build()
            self.document_repository.save_document(caution_doc, ID_REPO_BAUX)
