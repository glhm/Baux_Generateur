from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str = "France"

    def __str__(self) -> str:
        return f"{self.street}, {self.postal_code} {self.city}, {self.country}"

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "EUR"

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currencies must match for addition")
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

@dataclass(frozen=True)
class Period:
    start_date: date
    end_date: Optional[date] = None

    def includes(self, check_date: date) -> bool:
        if self.end_date:
            return self.start_date <= check_date <= self.end_date
        return self.start_date <= check_date
