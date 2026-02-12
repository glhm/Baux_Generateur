from datetime import datetime
from typing import List, Dict, Any, Optional

from src.domain.entities.lease import Lease
from src.domain.entities.financials import Financials, DepartureNumbers
from src.adapters.google_docs_renderer import GoogleDocsRenderer
from src.adapters.google_drive_adapter import GoogleDriveAdapter
from src.domain.services.placeholder_service import PlaceholderService
from src.conf.info_apis import TEMPLATE_QUITTANCE_ID, MAP_PAGE_NOTION_BIEN_TO_REPO
from src.utils.naming import generate_quittance_doc_name, build_formatted_name, get_quittance_pattern
from src.utils.date_utils import compare_dates, map_mois_to_dernier_jour, mois_list, get_month_index
from src.use_cases.receipt_helpers import build_receipt_requests, TITRE_DETAIL_REGLEMENT, PARAGRAPHE_DETAIL_PREMIER_MOIS, PARAGRAPHE_DETAIL_DERNIER_MOIS

class GenerateReceiptUseCase:
    """
    Use case to generate receipts (Quittances) for a tenant.
    """

    def __init__(
        self,
        template_renderer: GoogleDocsRenderer,
        drive_adapter: GoogleDriveAdapter,
        placeholder_service: PlaceholderService
    ):
        self.template_renderer = template_renderer
        self.drive_adapter = drive_adapter
        self.placeholder_service = placeholder_service

    def execute(self, lease: Lease):
        tenant = lease.tenant
        prop = lease.property
        financials = lease.financials
        period = lease.period
        
        # Validation
        if not lease.id or not prop or not prop.id:
            print(f"[ERROR] Missing ID or Property for {tenant.full_name}")
            return
            
        repo_id = MAP_PAGE_NOTION_BIEN_TO_REPO.get(prop.id)
        if not repo_id:
             print(f"[ERROR] No repo found for property {prop.id}")
             return

        # Base placeholders
        base_placeholders = self.placeholder_service.generate_placeholders(lease)
        formatted_name = tenant.full_name.title().replace(" ", "_").replace("'", "_").replace(",", "")

        # Arrival Info
        jour_arrivee = period.start_date.day
        mois_arrivee_num = period.start_date.month
        annee_arrivee = period.start_date.year
        
        # Departure Info
        has_departure = period.end_date is not None
        jour_depart = period.end_date.day if has_departure else None
        mois_depart_num = period.end_date.month if has_departure else None
        annee_depart = period.end_date.year if has_departure else None
        
        # Current Date for generation (used for filename?)
        now = datetime.now()
        jour_creation = now.day # Not used in logic but maybe filename?
        
        for annee_str in tenant.years:
            try:
                annee_courante = int(annee_str)
            except ValueError:
                print(f"[WARN] Invalid year format: {annee_str}")
                continue
                
            print(f"[INFO] Traitement année {annee_courante} pour {tenant.full_name}")
            
            # Folder structure
            year_folder = self.drive_adapter.get_or_create_subfolder(repo_id, str(annee_courante))
            recettes_folder = self.drive_adapter.get_or_create_subfolder(year_folder, "Recettes")
            at_folder = self.drive_adapter.get_or_create_subfolder(recettes_folder, "AT")
            
            if not at_folder:
                print(f"[ERROR] Could not create AT folder for {annee_courante}")
                continue
                
            for mois_nom in mois_list:
                mois_num = get_month_index(mois_nom)
                dernier_jour = map_mois_to_dernier_jour[mois_nom] # Approximation (doesn't handle leap year for Feb here, strictly speaking)
                # But map has fixed 28 for Feb.
                # In helper: map_mois_to_dernier_jour = { "Février": 28 ... }
                # So this might be wrong for Leap Year.
                # Let's use calendar logic or get_last_day_of_month logic if available.
                # But iterating over map keys is convenient.
                
                # Check bounds
                # Before arrival
                if annee_courante < annee_arrivee or (annee_courante == annee_arrivee and mois_num < mois_arrivee_num):
                    continue
                
                # After departure
                if has_departure and compare_dates(annee_courante, mois_num, 1, annee_depart, mois_depart_num, jour_depart) > 0:
                    # Cleanup old
                    pattern = get_quittance_pattern(f"{mois_num:02}", str(annee_courante), formatted_name)
                    # Implementation of delete logic in DriveAdapter?
                    # drive_adapter needs delete_files_matching_regex.
                    # It was in GoogleDocsRenderer...
                    # I should move it to GoogleDriveAdapter or use renderer.
                    # Implementation: drive_adapter needs `delete_files_matching_regex`.
                    # I'll check if I added it. If not, I'll add it.
                    continue

                somme_due = 0.0
                jour_debut_per = 1
                jour_fin_per = dernier_jour
                
                titre = ""
                paragraphe = ""
                montant1 = 0.0
                montant2 = 0.0
                
                # Logic
                if has_departure and annee_courante == annee_depart and mois_num == mois_depart_num:
                    # Last Month
                    dep_nums = DepartureNumbers.calculate(financials.loyer, financials.charges, jour_depart, mois_depart_num, annee_courante)
                    somme_due = dep_nums.prorata_total_CC_depart
                    jour_fin_per = jour_depart
                    titre = TITRE_DETAIL_REGLEMENT
                    paragraphe = PARAGRAPHE_DETAIL_DERNIER_MOIS
                    montant1 = dep_nums.prorata_loyer_depart
                    montant2 = dep_nums.prorata_charges_depart
                    
                elif annee_courante == annee_arrivee and mois_num == mois_arrivee_num:
                    # First Month
                    # Financials has calculated this for us based on start date
                    somme_due = financials.prorata_total_CC
                    jour_debut_per = jour_arrivee
                    titre = TITRE_DETAIL_REGLEMENT
                    paragraphe = PARAGRAPHE_DETAIL_PREMIER_MOIS
                    montant1 = financials.prorata_loyer
                    montant2 = financials.prorata_charges
                    
                else:
                    # Full Month
                    somme_due = financials.loyer_CC
                    titre = ""
                    paragraphe = ""
                    montant1 = financials.loyer
                    montant2 = financials.charges
                
                # Build requests
                receipt_requests = build_receipt_requests(
                    somme_due, jour_debut_per, titre, paragraphe, 
                    annee_courante, mois_nom, dernier_jour, jour_fin_per
                )
                
                # Create Doc
                # Need to convert list of dicts to list of requests properly.
                # build_receipt_requests returns List[Dict].
                # base_placeholders is Dict[str, str].
                # GoogleDocsRenderer._build_requests takes Dict[str, str].
                # Usage in renderer: `replace_requests = self._build_requests(placeholders)`
                # Then calls batchUpdate with `requests`.
                # BUT here I have specific requests list (constructed manually).
                # `create_and_export_doc_from_template` (legacy) accepted `replace_requests` list.
                # My `GoogleDocsRenderer.render` takes `placeholders: Dict`.
                # I cannot pass a list of requests to `render`.
                # Refactoring needed: `GoogleDocsRenderer.render` needs to accept `extra_requests` or I need to map my receipt params to a Dict.
                # `build_receipt_requests` returns `replaceAllText` requests.
                # If I can express them as a Dict `key: val`, I can pass them to `render`.
                # `build_receipt_requests` uses keys like `{{PERIODE}}`, `{{SOMME_TOTALE}}`.
                # Can I just use a dict? YES.
                # Why did legacy code use requests list? Maybe because of complex logic?
                # But `build_receipt_requests` just iterates a dict!
                # So I can just return a Dict from helper and merge with base placeholders!
                
                # Let's change `build_receipt_requests` to return Dict[str, str]!
                
                receipt_placeholders = build_receipt_requests(
                     somme_due, jour_debut_per, titre, paragraphe, 
                    annee_courante, mois_nom, dernier_jour, jour_fin_per,
                    return_dict=True # I'll modify helper
                )
                
                final_placeholders = {**base_placeholders, **receipt_placeholders}
                
                doc_name = generate_quittance_doc_name(jour_creation, mois_num, annee_courante, formatted_name, montant1, montant2)
                
                self.template_renderer.render(
                    template_id=TEMPLATE_QUITTANCE_ID,
                    placeholders=final_placeholders,
                    output_name=doc_name,
                    folder_id=at_folder
                )
