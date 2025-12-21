import os
import sys

# Ensure src is in pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.infrastructure.logging.logger import StandardLogger
from src.infrastructure.adapters.notion_tenant_repository import NotionTenantRepository
from src.infrastructure.adapters.notion_property_repository import NotionPropertyRepository
from src.infrastructure.adapters.notion_financial_repositories import NotionRentRepository, NotionRoomRepository
from src.infrastructure.adapters.notion_guarantor_repository import NotionGuarantorRepository
from src.infrastructure.adapters.google_drive_adapter import GoogleDriveAdapter
from src.application.use_cases.generate_lease import GenerateLeaseUseCase
from src.application.use_cases.process_tenant_actions import ProcessTenantActionUseCase

logger = StandardLogger()

def lambda_handler(event, context):
    """
    AWS Lambda Entry Point.
    """
    try:
        logger.info("Lambda execution started.")
        
        # Dependency Injection
        # Configuration (Env vars)
        notion_db_id = os.getenv("NOTION_DATABASE_ID", "default_db_id")
        # Notion IDs might be separate for each "Table" in real life
        # For now, sharing the same ID variable or we'd load separate ones
        
        # Adapters
        tenant_repo = NotionTenantRepository(database_id=notion_db_id)
        property_repo = NotionPropertyRepository(database_id=notion_db_id)
        rent_repo = NotionRentRepository(database_id=notion_db_id)
        room_repo = NotionRoomRepository(database_id=notion_db_id)
        guarantor_repo = NotionGuarantorRepository(database_id=notion_db_id)
        drive_adapter = GoogleDriveAdapter()
        
        # Use Cases
        generate_lease_uc = GenerateLeaseUseCase(
            tenant_repository=tenant_repo,
            property_repository=property_repo,
            rent_repository=rent_repo,
            document_service=drive_adapter,
            logger=logger
        )
        
        process_actions_uc = ProcessTenantActionUseCase(
            tenant_repo=tenant_repo,
            generate_lease_use_case=generate_lease_uc,
            logger=logger
        )
        
        # Execute
        process_actions_uc.execute()
        
        logger.info("Lambda execution finished successfully.")
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        logger.error(f"Global Error Handler caught exception: {e}", exc_info=True)
        return {"statusCode": 500, "body": str(e)}

if __name__ == "__main__":
    # Local execution simulation
    lambda_handler({}, {})
