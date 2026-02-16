from dataclasses import dataclass

from src.domain.entities.financials import Financials
from src.domain.entities.guarantor import Guarantor, PhysicalGuarantor, VisaleGuarantor
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.tenant import Tenant
from src.domain.entities.value_objects import Period


@dataclass
class Lease:
    """Represents a lease aggregate used by the application use cases."""

    tenant: Tenant
    property: Property
    room: Room
    financials: Financials
    guarantor: Guarantor
    period: Period
    type_bail: str
    date_fin_theorique: str
    mention_speciale: str
    id: str = ""

    def is_visale_guarantor(self) -> bool:
        return isinstance(self.guarantor, VisaleGuarantor)

    def is_physical_guarantor(self) -> bool:
        return isinstance(self.guarantor, PhysicalGuarantor)

    class Builder:
        def __init__(self):
            self._id = ""
            self._tenant = None
            self._property = None
            self._room = None
            self._financials = None
            self._guarantor = None
            self._period = None
            self._type_bail = ""
            self._date_fin_theorique = ""
            self._mention_speciale = ""

        def with_id(self, lease_id: str) -> 'Lease.Builder':
            self._id = lease_id
            return self

        def with_tenant(self, tenant: Tenant) -> 'Lease.Builder':
            self._tenant = tenant
            return self

        def with_property(self, prop: Property) -> 'Lease.Builder':
            self._property = prop
            return self

        def with_room(self, room: Room) -> 'Lease.Builder':
            self._room = room
            return self

        def with_financials(self, financials: Financials) -> 'Lease.Builder':
            self._financials = financials
            return self

        def with_guarantor(self, guarantor: Guarantor) -> 'Lease.Builder':
            self._guarantor = guarantor
            return self

        def with_period(self, period: Period) -> 'Lease.Builder':
            self._period = period
            return self

        def with_type_bail(self, type_bail: str) -> 'Lease.Builder':
            self._type_bail = type_bail
            return self

        def with_date_fin_theorique(self, date_fin: str) -> 'Lease.Builder':
            self._date_fin_theorique = date_fin
            return self

        def with_mention_speciale(self, mention: str) -> 'Lease.Builder':
            self._mention_speciale = mention
            return self

        def build(self) -> 'Lease':
            if self._tenant is None:
                raise ValueError("Lease must have a Tenant")
            if self._property is None:
                raise ValueError("Lease must have a Property")
            if self._room is None:
                raise ValueError("Lease must have a Room")
            if self._financials is None:
                raise ValueError("Lease must have Financials")
            if self._guarantor is None:
                raise ValueError("Lease must have a Guarantor")
            if self._period is None:
                raise ValueError("Lease must have a Period")
            if not self._type_bail:
                raise ValueError("Lease must have a Type Bail")
            if not self._date_fin_theorique:
                raise ValueError("Lease must have a Date Fin Theorique")

            return Lease(
                id=self._id,
                tenant=self._tenant,
                property=self._property,
                room=self._room,
                financials=self._financials,
                guarantor=self._guarantor,
                period=self._period,
                type_bail=self._type_bail,
                date_fin_theorique=self._date_fin_theorique,
                mention_speciale=self._mention_speciale,
            )
