class DomainException(Exception):
    """Base class for domain exceptions."""
    pass

class TenantNotFoundException(DomainException):
    def __init__(self, tenant_name: str):
        super().__init__(f"Tenant '{tenant_name}' not found.")

class LeaseGenerationException(DomainException):
    def __init__(self, message: str):
        super().__init__(f"Lease generation failed: {message}")

class InfrastructureException(DomainException):
    """Wraps infrastructure level errors."""
    pass
