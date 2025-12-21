from src.domain.ports.repositories import TenantRepository, PropertyRepository, RentRepository
from src.domain.ports.services import DocumentService, LoggerPort
from src.domain.entities.lease import Lease
from src.domain.entities.financials import Numbers
from src.domain.strategies.lease_strategy import LeaseStrategyFactory
from src.application.commands import GenerateLeaseCommand
from src.domain.exceptions.custom_exceptions import TenantNotFoundException, LeaseGenerationException
from datetime import date
import logging
from src.application.mappers.google_doc_mapper import GoogleDocMapper
from src.domain.entities.document import Document

class GenerateLeaseUseCase:
    def __init__(self, 
                 tenant_repository: TenantRepository, 
                 property_repository: PropertyRepository,
                 rent_repository: RentRepository,
                 document_service: DocumentService,
                 logger: LoggerPort):
        self.tenant_repo = tenant_repository
        self.property_repo = property_repository
        self.rent_repo = rent_repository
        self.doc_service = document_service
        self.logger = logger

    def execute(self, command: GenerateLeaseCommand) -> str:
        self.logger.info(f"Starting lease generation for {command.tenant_name}")

        tenant = self.tenant_repo.get_tenant_by_name(command.tenant_name)
        if not tenant:
            self.logger.error(f"Tenant {command.tenant_name} not found")
            raise TenantNotFoundException(command.tenant_name)

        property_obj = self.property_repo.get_property_by_name(command.property_name)
        if not property_obj:
             raise LeaseGenerationException(f"Property {command.property_name} not found")

        # Fetch Financial Data (Rent) - Assuming linked by Tenant or Property Name? 
        # For this refactor, let's assume we find it by Property Name or similar.
        # Ideally, we'd have an ID link.
        rent_data = self.rent_repo.get_rent_by_name(command.property_name) # Using property name as key for rent lookup
        
        if not rent_data:
             # Fallback or error
             self.logger.warning(f"Rent data for {command.property_name} not found, using defaults.")
             loyer_amount = 600.0
             charges_amount = 50.0
        else:
             # Extract from entity/dict (assuming Rent entity has these fields)
             loyer_amount = rent_data.get('loyer', 600.0)
             charges_amount = rent_data.get('charges', 50.0)

        # Calculate Financials using Domain Logic
        # Parse command dates
        start_date = date.fromisoformat(command.start_date)
        
        # Calculate financials (prorata, etc.)
        # Need "mois_arrivee_str" - derive from start_date
        # French month names...
        french_months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        month_str = french_months[start_date.month - 1]
        
        financials = Numbers.calculate(
            loyer_amount=loyer_amount,
            charges_amount=charges_amount,
            jour_arrivee=start_date.day,
            mois_arrivee_str=month_str
        )

        strategy = LeaseStrategyFactory.get_strategy(property_obj.furniture_type)
        
        try:
            builder = Lease.Builder()\
                .with_tenant(tenant)\
                .with_property(property_obj)\
                .with_period(start_date)\
                .with_rent(financials.loyer)\
                .with_charges(financials.charges)\
                .with_deposit(financials.montant_garanties)

            strategy.customize_lease(builder)
            
            lease = builder.build()
            
            # Hydrate Tenant for Mapper logic (should ideally be done in a Domain Service or Repo)
            tenant.financials = financials
            tenant.property_obj = property_obj
            
            # Generate Document using Mapper
            replacements = GoogleDocMapper.get_lease_placeholders(tenant)
            
            # Template ID should come from configuration or Property details
            template_id = "YOUR_LEASE_TEMPLATE_ID" 
            doc_name = f"Bail - {tenant.full_name}"
            
            document = Document.Builder()\
                .with_name(doc_name)\
                .with_template_id(template_id)\
                .with_replacements(replacements)\
                .build()
                
            doc_id = self.doc_service.generate_document(document)
            
            self.logger.info(f"Lease generated successfully for {command.tenant_name}, Drive ID: {doc_id}")
            return doc_id

        except Exception as e:
            self.logger.error(f"Error generating lease: {str(e)}")
            raise LeaseGenerationException(str(e))
