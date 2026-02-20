from src.adapters.notion_adapter import NotionAdapter
from src.adapters.google_auth_provider import GoogleAuthProvider
from src.adapters.google_docs_renderer import GoogleDocsRenderer
#from src.adapters.gmail_adapter import GmailAdapter
from src.adapters.google_drive_adapter import GoogleDriveAdapter
from src.domain.services.placeholder_service import PlaceholderService
from src.domain.template_config import LeaseTemplateConfig
from src.conf.info_apis import ID_TEMPLATE_BAIL_MEUBLE, CAUTION_ID
from src.use_cases.generate_lease_use_case import GenerateLeaseUseCase
from src.use_cases.generate_receipt_use_case import GenerateReceiptUseCase

def do_tasks_required_from_user():
    # 1. Initialize Adapters & Services
    auth_provider = GoogleAuthProvider()
    
    notion_repo: LeaseRepository = NotionAdapter()  
    template_renderer = GoogleDocsRenderer(auth_provider)
   # gmail_adapter = GmailAdapter(auth_provider)
    drive_adapter = GoogleDriveAdapter(auth_provider)
    placeholder_service = PlaceholderService()
    lease_template_config = LeaseTemplateConfig(
        bail_template_id=ID_TEMPLATE_BAIL_MEUBLE,
        caution_template_id=CAUTION_ID,
    )
    
    # 2. Retrieve Leases via Repository (port)
    print("[INFO] Fetching leases from Notion repository...")
    leases = notion_repo.get_all_concerned_leases()
    
    # 3. Process each lease
    for lease in leases:
        tenant = lease.tenant
        if not tenant:
            continue

        # A. Lease Generation
        if tenant.activer_generation: 
            print(f"[INFO] Processing lease for {tenant.full_name}")
            generate_lease_use_case = GenerateLeaseUseCase(template_renderer, placeholder_service, lease_template_config)
            generate_lease_use_case.execute(lease)

        # B. Receipt Generation
        if tenant.activer_generation_quittances:
            print(f"[INFO] Processing receipt generation for {tenant.full_name}")
            generate_receipt_use_case = GenerateReceiptUseCase(template_renderer, drive_adapter, placeholder_service)
            generate_receipt_use_case.execute(lease)
            
        # C. Receipt Sending
        # if tenant.envoyer_quittance:
    
        #     send_receipt_use_case = SendReceiptUseCase(gmail_adapter, drive_adapter, notion_repo)
        #     send_receipt_use_case.execute(lease)

