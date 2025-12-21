from dataclasses import dataclass
from src.domain.entities.tenant import Tenant
from src.domain.entities.property import Property
from src.domain.entities.value_objects import Period, Money

@dataclass
class GenerateLeaseCommand:
    tenant_name: str
    property_name: str
    start_date: str # ISO format YYYY-MM-DD
    # Add other necessary fields required to triggering the generation if they come from the user input/trigger

@dataclass
class GenerateReceiptCommand:
    tenant_name: str
    period_start: str
    period_end: str

@dataclass
class SendReceiptCommand:
    tenant_name: str
    receipt_path: str
