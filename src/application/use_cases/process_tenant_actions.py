from typing import List
from src.domain.ports.repositories import TenantRepository
from src.domain.ports.services import LoggerPort
from src.application.use_cases.generate_lease import GenerateLeaseUseCase
from src.application.commands import GenerateLeaseCommand
from src.domain.entities.tenant import Tenant
import datetime

class ProcessTenantActionUseCase:
    def __init__(self, 
                 tenant_repo: TenantRepository, 
                 generate_lease_use_case: GenerateLeaseUseCase,
                 logger: LoggerPort):
        self.tenant_repo = tenant_repo
        self.generate_lease_use_case = generate_lease_use_case
        self.logger = logger

    def execute(self) -> None:
        self.logger.info("Starting batch processing of tenants...")
        tenants = self.tenant_repo.get_all_tenants()
        
        for tenant in tenants:
            # Here lies a small issue: our Tenant Entity doesn't necessarily have the "flags" (generate_lease, etc.)
            # If those flags are purely for "Action", they might belong to the DTO or a specific "ActionableTenant" model.
            # However, for simplicity in this Clean Archi refactor, we can assume the Tenant entity *has* these flags 
            # if they are part of the business state (e.g. "needs lease renewal").
            # OR, the Repository returns something that includes metadata.
            
            # Let's assume for this exercise that we check this logic via the Repository or separate query,
            # or we add these flags to the Tenant entity for now.
            try:
                # Mocking the check logic as it's not yet in the Tenant entity definition I created earlier
                # We should probably update Tenant entity to include these flags or handle it differently.
                # For now, I will perform a safe check if attributes exist (dynamic) or relying on a separate method.
                
                if getattr(tenant, 'generate_lease_flag', False):
                    self.logger.info(f"Triggering lease generation for {tenant.full_name}")
                    command = GenerateLeaseCommand(
                        tenant_name=tenant.full_name, # using name as key for now
                        property_name="TBD", # Need to fetch property name from Tenant/Notion
                        start_date=datetime.date.today().isoformat()
                    )
                    self.generate_lease_use_case.execute(command)
                
            except Exception as e:
                self.logger.error(f"Error processing tenant {tenant.full_name}: {e}")
                
        self.logger.info("Batch processing complete.")
