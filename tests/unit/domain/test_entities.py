import pytest
from datetime import date
from src.domain.entities.lease import Lease
from src.domain.entities.tenant import Tenant
from src.domain.entities.property import Property
from src.domain.entities.value_objects import Address, Money, Period

def test_lease_builder_and_calculations():
    # Arrange
    addr = Address("1 Rue Paix", "Paris", "75000")
    tenant = Tenant("John", "Doe", "john@mail.com", "060000", addr)
    prop = Property("Apt 1", addr, "Meublé", "Desc", "Owner")
    
    # Act
    lease = Lease.Builder()\
        .with_tenant(tenant)\
        .with_property(prop)\
        .with_period(date(2023, 1, 1), date(2023, 12, 31))\
        .with_rent(1000.0)\
        .with_charges(100.0)\
        .with_deposit(2000.0)\
        .build()
        
    # Assert
    assert lease.tenant == tenant
    assert lease.rent.amount == 1000.0
    assert lease.charges.amount == 100.0
    assert lease.total_rent.amount == 1100.0
    assert lease.period.start_date == date(2023, 1, 1)

def test_lease_builder_missing_fields():
    # Act & Assert
    with pytest.raises(ValueError):
        Lease.Builder().with_rent(500.0).build()
