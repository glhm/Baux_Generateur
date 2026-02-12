from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from src.adapters.google_docs_renderer import GoogleDocsRenderer
from src.adapters.google_drive_adapter import GoogleDriveAdapter
from src.conf.info_apis import MAP_PAGE_NOTION_BIEN_TO_REPO, TEMPLATE_QUITTANCE_ID
from src.domain.entities.financials import DepartureNumbers
from src.domain.entities.lease import Lease
from src.domain.services.placeholder_service import PlaceholderService
from src.use_cases.receipt_helpers import (
    PARAGRAPHE_DETAIL_DERNIER_MOIS,
    PARAGRAPHE_DETAIL_PREMIER_MOIS,
    TITRE_DETAIL_REGLEMENT,
    build_receipt_requests,
)
from src.utils.date_utils import compare_dates, get_month_index, map_mois_to_dernier_jour, mois_list
from src.utils.naming import generate_quittance_doc_name, get_quittance_pattern


class ReceiptMonthKind(Enum):
    FIRST = "first"
    FULL = "full"
    LAST = "last"


@dataclass(frozen=True)
class ReceiptComputation:
    amount_due: float
    start_day: int
    end_day: int
    title: str
    paragraph: str
    rent_amount: float
    charges_amount: float


class ReceiptAmountPolicy:
    """Strategy object to compute receipt amounts depending on month type."""

    @staticmethod
    def for_month(
        month_kind: ReceiptMonthKind,
        *,
        lease: Lease,
        year: int,
        month_num: int,
        last_day_of_month: int,
        arrival_day: int,
        departure_day: Optional[int],
    ) -> ReceiptComputation:
        financials = lease.financials

        if month_kind == ReceiptMonthKind.LAST:
            if departure_day is None:
                raise ValueError("departure_day is required for LAST month computation")

            departure_numbers = DepartureNumbers.calculate(
                financials.loyer,
                financials.charges,
                departure_day,
                month_num,
                year,
            )
            return ReceiptComputation(
                amount_due=departure_numbers.prorata_total_CC_depart,
                start_day=1,
                end_day=departure_day,
                title=TITRE_DETAIL_REGLEMENT,
                paragraph=PARAGRAPHE_DETAIL_DERNIER_MOIS,
                rent_amount=departure_numbers.prorata_loyer_depart,
                charges_amount=departure_numbers.prorata_charges_depart,
            )

        if month_kind == ReceiptMonthKind.FIRST:
            return ReceiptComputation(
                amount_due=financials.prorata_total_CC,
                start_day=arrival_day,
                end_day=last_day_of_month,
                title=TITRE_DETAIL_REGLEMENT,
                paragraph=PARAGRAPHE_DETAIL_PREMIER_MOIS,
                rent_amount=financials.prorata_loyer,
                charges_amount=financials.prorata_charges,
            )

        return ReceiptComputation(
            amount_due=financials.loyer_CC,
            start_day=1,
            end_day=last_day_of_month,
            title="",
            paragraph="",
            rent_amount=financials.loyer,
            charges_amount=financials.charges,
        )


class GenerateReceiptUseCase:
    """Generate monthly rent receipts for a lease according to selected years."""

    def __init__(
        self,
        template_renderer: GoogleDocsRenderer,
        drive_adapter: GoogleDriveAdapter,
        placeholder_service: PlaceholderService,
    ):
        self.template_renderer = template_renderer
        self.drive_adapter = drive_adapter
        self.placeholder_service = placeholder_service

    def execute(self, lease: Lease) -> None:
        tenant = lease.tenant
        prop = lease.property
        period = lease.period

        if not lease.id or not prop or not prop.id:
            print(f"[ERROR] Missing lease id or property id for {tenant.full_name}")
            return

        repo_id = MAP_PAGE_NOTION_BIEN_TO_REPO.get(prop.id)
        if not repo_id:
            print(f"[ERROR] No repository mapping found for property {prop.id}")
            return

        base_placeholders = self.placeholder_service.generate_placeholders(lease)
        formatted_name = tenant.full_name.title().replace(" ", "_").replace("'", "_").replace(",", "")

        arrival_day = period.start_date.day
        arrival_month = period.start_date.month
        arrival_year = period.start_date.year

        has_departure = period.end_date is not None
        departure_day = period.end_date.day if has_departure else None
        departure_month = period.end_date.month if has_departure else None
        departure_year = period.end_date.year if has_departure else None

        generation_day = datetime.now().day

        for selected_year in tenant.years:
            try:
                current_year = int(selected_year)
            except ValueError:
                print(f"[WARN] Invalid selected year '{selected_year}' for {tenant.full_name}")
                continue

            at_folder = self._get_target_folder(repo_id, current_year)
            if not at_folder:
                print(f"[ERROR] AT folder unavailable for year {current_year}")
                continue

            for month_name in mois_list:
                month_num = get_month_index(month_name)

                if self._is_before_arrival(current_year, month_num, arrival_year, arrival_month):
                    continue

                if has_departure and self._is_after_departure(current_year, month_num, departure_year, departure_month, departure_day):
                    pattern = get_quittance_pattern(f"{month_num:02}", str(current_year), formatted_name)
                    self.drive_adapter.delete_files_matching_regex(at_folder, pattern)
                    continue

                month_kind, last_day = self._resolve_month_kind(
                    current_year,
                    month_num,
                    month_name,
                    arrival_year,
                    arrival_month,
                    has_departure,
                    departure_year,
                    departure_month,
                )

                computation = ReceiptAmountPolicy.for_month(
                    month_kind,
                    lease=lease,
                    year=current_year,
                    month_num=month_num,
                    last_day_of_month=last_day,
                    arrival_day=arrival_day,
                    departure_day=departure_day,
                )

                receipt_placeholders = build_receipt_requests(
                    somme_due=computation.amount_due,
                    jour_debut=computation.start_day,
                    titre_detail=computation.title,
                    paragraphe_detail=computation.paragraph,
                    annee=current_year,
                    mois_nom=month_name,
                    dernier_jour_mois=last_day,
                    jour_fin=computation.end_day,
                )

                final_placeholders = {**base_placeholders, **receipt_placeholders}
                output_name = generate_quittance_doc_name(
                    generation_day,
                    month_num,
                    current_year,
                    formatted_name,
                    computation.rent_amount,
                    computation.charges_amount,
                )

                self.template_renderer.render(
                    template_id=TEMPLATE_QUITTANCE_ID,
                    placeholders=final_placeholders,
                    output_name=output_name,
                    folder_id=at_folder,
                )

    def _get_target_folder(self, repo_id: str, year: int) -> Optional[str]:
        year_folder = self.drive_adapter.get_or_create_subfolder(repo_id, str(year))
        recettes_folder = self.drive_adapter.get_or_create_subfolder(year_folder, "Recettes")
        return self.drive_adapter.get_or_create_subfolder(recettes_folder, "AT")

    @staticmethod
    def _is_before_arrival(current_year: int, month_num: int, arrival_year: int, arrival_month: int) -> bool:
        return current_year < arrival_year or (current_year == arrival_year and month_num < arrival_month)

    @staticmethod
    def _is_after_departure(
        current_year: int,
        month_num: int,
        departure_year: Optional[int],
        departure_month: Optional[int],
        departure_day: Optional[int],
    ) -> bool:
        if departure_year is None or departure_month is None or departure_day is None:
            return False
        return compare_dates(current_year, month_num, 1, departure_year, departure_month, departure_day) > 0

    @staticmethod
    def _resolve_month_kind(
        current_year: int,
        month_num: int,
        month_name: str,
        arrival_year: int,
        arrival_month: int,
        has_departure: bool,
        departure_year: Optional[int],
        departure_month: Optional[int],
    ) -> Tuple[ReceiptMonthKind, int]:
        last_day = map_mois_to_dernier_jour[month_name]

        if has_departure and current_year == departure_year and month_num == departure_month:
            return ReceiptMonthKind.LAST, last_day

        if current_year == arrival_year and month_num == arrival_month:
            return ReceiptMonthKind.FIRST, last_day

        return ReceiptMonthKind.FULL, last_day
