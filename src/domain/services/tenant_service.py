from typing import List
from src.domain.ports.tenant_repository import TenantRepository
from src.domain.entities.tenant import Tenant


class TenantService:

    def __init__(self, tenant_repository: TenantRepository):
        self._tenant_repository = tenant_repository

    def get_concerned_tenants(self) -> List[Tenant]:
        return self._tenant_repository.get_all_concerned_tenants()
