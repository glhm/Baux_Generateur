from dataclasses import dataclass, field
from typing import List
from datetime import date
from src.domain.entities.tenant import Tenant
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.guarantor import Guarantor
from src.domain.entities.financials import Financials
from src.domain.entities.value_objects import Period

@dataclass
class Lease:
    """Represents a Lease (Bail) aggregate."""
    id: str = "" # Notion Page ID (Locataire)
    tenant: Tenant
    property: Property
    room: Room
    financials: Financials
    guarantor: Guarantor
    period: Period
    
    #type_garantie: GuarantorType TODO Dlete ?
    type_bail: LeaseType
    
    # Specific fields moved from Tenant
    date_fin_theorique: str
    mention_speciale: str
    
    def is_visale_guarantor(self) -> bool:
        return isinstance(self.guarantor, VisaleGuarantor)

    def is_physical_guarantor(self) -> bool:
        return isinstance(self.guarantor, PhysicalGuarantor)
    class Builder:
        def __init__(self):
            self._id = ""
            self._tenant: Tenant = None # type: ignore
            self._property: Property = None # type: ignore
            self._room: Room = None # type: ignore
            self._financials: Financials = None # type: ignore
            self._guarantor: Guarantor = None # type: ignore
            self._period: Period = None # type: ignore
            self._type_garantie: GuarantorType = None # type: ignore
            self._type_bail: LeaseType = None # type: ignore
            self._date_fin_theorique: str = ""
            self._mention_speciale: str = ""
        
        def with_id(self, id: str) -> 'Lease.Builder':
            self._id = id
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

        def with_financials(self, stats: Financials) -> 'Lease.Builder':
            self._financials = stats
            return self

        def with_guarantor(self, guarantor: Guarantor) -> 'Lease.Builder':
            self._guarantor = guarantor
            return self
        
        def with_period(self, period: Period) -> 'Lease.Builder':
            self._period = period
            return self


        def with_date_fin_theorique(self, date_fin: str) -> 'Lease.Builder':
                self._date_fin_theorique = date_fin
                return self

        def with_mention_speciale(self, mention: str) -> 'Lease.Builder':
            self._mention_speciale = mention
            return self
            
        def build(self) -> 'Lease':
            # Enforce required fields
            if not self._tenant: raise ValueError("Lease must have a Tenant")
            if not self._property: raise ValueError("Lease must have a Property")
            # Room? If user says non-optional, we check it.
            if not self._room: raise ValueError("Lease must have a Room") 
            if not self._financials: raise ValueError("Lease must have Financials")
            if not self._period: raise ValueError("Lease must have a Period")
            if not self._guarantor: raise ValueError("Lease must have a Guarantor")
            if not self.date_fin_theorique: raise ValueError("Lease must have a Date Fin Theorique")
            # type_garantie? Not explicitly listed as non-optional in the snippet I copied?
            # User said "aucun de ces champs ne sont optionnels".
            # Referencing the list they pasted. 
            # I added type_garantie myself.
            # But normally type_garantie is required for logic.
            if not self._type_bail: raise ValueError("Lease must have a Type Bail")
            
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
                mention_speciale=self._mention_speciale
            )
