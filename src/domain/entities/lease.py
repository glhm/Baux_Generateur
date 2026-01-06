from dataclasses import dataclass
from typing import Optional
from datetime import date
from src.domain.entities.tenant import Tenant
from src.domain.entities.property import Property
from src.domain.entities.value_objects import Money, Period

@dataclass
class Lease:
    tenant: Tenant
    property: Property
    period: Period
    rent: Money
    charges: Money
    deposit: Money
    signed_date: Optional[date] = None

    @property
    def total_rent(self) -> Money:
        return self.rent + self.charges

    class Builder:
        def __init__(self):
            self._tenant: Optional[Tenant] = None
            self._property: Optional[Property] = None
            self._period: Optional[Period] = None
            self._rent: Optional[Money] = None
            self._charges: Optional[Money] = None
            self._deposit: Optional[Money] = None
        
        def with_tenant(self, tenant: Tenant) -> 'Lease.Builder':
            self._tenant = tenant
            return self
        
        def with_property(self, prop: Property) -> 'Lease.Builder':
            self._property = prop
            return self
        
        def with_period(self, start_date: date, end_date: Optional[date] = None) -> 'Lease.Builder':
            self._period = Period(start_date, end_date)
            return self
        
        def with_rent(self, amount: float) -> 'Lease.Builder':
            self._rent = Money(amount)
            return self
            
        def with_charges(self, amount: float) -> 'Lease.Builder':
            self._charges = Money(amount)
            return self

        def with_deposit(self, amount: float) -> 'Lease.Builder':
            self._deposit = Money(amount)
            return self

        def build(self) -> 'Lease':
            if not all([self._tenant, self._property, self._period, self._rent, self._charges, self._deposit]):
                raise ValueError("Missing required lease information")
            # mypy checks would fail without assertions/checks here, but at runtime this is safe assumes not None
            return Lease(
                tenant=self._tenant, # type: ignore
                property=self._property, # type: ignore
                period=self._period, # type: ignore
                rent=self._rent, # type: ignore
                charges=self._charges, # type: ignore
                deposit=self._deposit # type: ignore
            )
