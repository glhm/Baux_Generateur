from src.adapters.notion_adapter import NotionAdapter
from src.adapters.google_auth_provider import GoogleAuthProvider
from src.adapters.google_docs_renderer import GoogleDocsRenderer
from src.domain.services.placeholder_service import PlaceholderService
from src.services.tenant_service import TenantService
from src.use_cases.generate_lease_use_case import GenerateLeaseUseCase

def do_tasks_required_from_user():
    # 1. Initialize Adapters & Services
    auth_provider = GoogleAuthProvider()
    tenant_repository = NotionAdapter()
    tenant_service = TenantService(tenant_repository)
    template_renderer = GoogleDocsRenderer(auth_provider)
    placeholder_service = PlaceholderService()
    
    # 2. Retrieve Tenants via TenantService
    print("[INFO] Fetching tenants from Notion...")
    tenants = tenant_service.get_concerned_tenants()
    
    # 3. Process each tenant
    for tenant in tenants:
        # Filter: only if generation is requested
        if tenant.activer_generation: 
            print(f"[INFO] Processing lease for {tenant.full_name}")
            generate_lease_use_case = GenerateLeaseUseCase(template_renderer, placeholder_service)
            generate_lease_use_case.execute(tenant)

        # TODO: Handle Receipts Use Cases here similarly
