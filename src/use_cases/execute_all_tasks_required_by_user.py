from src.adapters.notion_adapter import NotionAdapter
from src.adapters.google_drive_adapter import GoogleDriveAdapter
from src.domain.services.placeholder_service import PlaceholderService
from src.use_cases.generate_lease_use_case import GenerateLeaseUseCase

def do_tasks_required_from_user():
    # 1. Initialize Adapters & Services
    tenant_repository = NotionAdapter()
    document_repository = GoogleDriveAdapter()
    placeholder_service = PlaceholderService()
    
    # Initialize Use Cases
    generate_lease_use_case = GenerateLeaseUseCase(document_repository, placeholder_service)
    
    # 2. Retrieve Tenants
    print("[INFO] Fetching tenants from Notion...")
    tenants = tenant_repository.get_tenants()
    
    # 3. Process each tenant
    for tenant in tenants:
        # Filter: only if generation is requested
        if tenant.activer_generation: 
            print(f"[INFO] Processing lease for {tenant.full_name}")
            generate_lease_use_case.execute(tenant)

        # TODO: Handle Receipts Use Cases here similarly
