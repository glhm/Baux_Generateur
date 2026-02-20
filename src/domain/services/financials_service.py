from src.domain.entities.financials import Financials
from src.domain.entities.lease import Lease


MONTHS_FR_REVERSE = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}


class FinancialsService:
    """Domain service that computes prorata financials for a Lease aggregate."""

    @staticmethod
    def compute_prorata(lease: Lease) -> Financials:
        """
        Compute the full Financials (with prorata) from the base
        loyer/charges already attached to the lease and its arrival date.

        Returns the enriched Financials, or the original one unchanged
        when the period information is missing.
        """
        fin = lease.financials
        period = lease.period

        if not fin or not period or not period.start_date:
            return fin

        sd = period.start_date
        mois_str = MONTHS_FR_REVERSE.get(sd.month, "Janvier")

        return Financials.calculate(
            loyer_amount=fin.loyer,
            charges_amount=fin.charges,
            jour_arrivee=sd.day,
            mois_arrivee_str=mois_str,
            year=sd.year,
        )
