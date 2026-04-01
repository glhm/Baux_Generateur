from dataclasses import dataclass, field
from typing import Dict, Optional
import calendar

# Mapping of French month names to days in that month (simplified standard, could be improved with calendar module)
# Actually, the original code had a map. Let's reproduce or use logic.
MONTH_MAP = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6,
    "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}

def get_last_day_of_month(month_name: str, year: int = 2024) -> int: # Year default or derived?
    month_num = MONTH_MAP.get(month_name)
    if not month_num:
        return 30 # Fallback
    return calendar.monthrange(year, month_num)[1]

def get_last_day_of_month_index(month_index: int, year: int = 2024) -> int:
    return calendar.monthrange(year, month_index)[1]


@dataclass(frozen=True)
class Financials:
    prorata_total_CC: float
    prorata_loyer: float
    prorata_charges: float
    nombre_de_jours_premier_mois: int
    total_premier_mois: float
    montant_garanties: float
    loyer_CC: float
    loyer: float
    charges: float

    @staticmethod
    def from_base_amounts(loyer_amount: float, charges_amount: float) -> 'Financials':
        """
        Build a Financials object from raw rent/charges only.
        Prorata-related fields are intentionally left to 0 and computed later
        by the dedicated domain service.
        """
        loyer_CC = loyer_amount + charges_amount
        return Financials(
            prorata_total_CC=0.0,
            prorata_loyer=0.0,
            prorata_charges=0.0,
            nombre_de_jours_premier_mois=0,
            total_premier_mois=0.0,
            montant_garanties=round(2 * loyer_amount, 2),
            loyer_CC=loyer_CC,
            loyer=loyer_amount,
            charges=charges_amount,
        )

    @staticmethod
    def calculate(loyer_amount: float, charges_amount: float, jour_arrivee: int, mois_arrivee_str: str, year: int = 2024) -> 'Financials':
        loyer_CC = loyer_amount + charges_amount
        
        last_day = get_last_day_of_month(mois_arrivee_str, year) # Requires context of year, assuming current or next
        
        nb_jours = last_day - jour_arrivee + 1
        ratio = nb_jours / last_day if last_day > 0 else 0
        
        prorata_total_CC = round(ratio * loyer_CC, 2)
        prorata_loyer = round(ratio * loyer_amount, 2)
        prorata_charges = round(ratio * charges_amount, 2)
        
        total_premier_mois = round(prorata_total_CC + 2 * loyer_amount, 2) # As per original logic: prorata + 2*loyer (caution?)
        montant_garanties = round(2 * loyer_amount, 2)
        
        return Financials(
            prorata_total_CC=prorata_total_CC,
            prorata_loyer=prorata_loyer,
            prorata_charges=prorata_charges,
            nombre_de_jours_premier_mois=nb_jours,
            total_premier_mois=total_premier_mois,
            montant_garanties=montant_garanties,
            loyer_CC=loyer_CC,
            loyer=loyer_amount,
            charges=charges_amount
        )

@dataclass(frozen=True)
class DepartureNumbers:
    prorata_total_CC_depart: float
    prorata_loyer_depart: float
    prorata_charges_depart: float

    @staticmethod
    def calculate(loyer_amount: float, charges_amount: float, jour_depart: int, mois_depart_num: int, year: int) -> 'DepartureNumbers':
        loyer_CC = loyer_amount + charges_amount
        
        last_day = get_last_day_of_month_index(mois_depart_num, year)
        ratio = jour_depart / last_day if last_day > 0 else 0
        
        return DepartureNumbers(
            prorata_total_CC_depart=round(ratio * loyer_CC, 2),
            prorata_loyer_depart=round(ratio * loyer_amount, 2),
            prorata_charges_depart=round(ratio * charges_amount, 2)
        )
