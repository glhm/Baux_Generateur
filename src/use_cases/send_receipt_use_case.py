from datetime import datetime
import os
from typing import Optional

from src.domain.entities.lease import Lease
from src.adapters.gmail_adapter import GmailAdapter
from src.adapters.google_drive_adapter import GoogleDriveAdapter
from src.adapters.notion_adapter import NotionAdapter
from src.conf.info_apis import QUITTANCE_RESULT_IDS, MAP_PAGE_NOTION_BIEN_TO_REPO
from src.utils.naming import get_quittance_pattern, build_formatted_name

class SendReceiptUseCase:

    def __init__(
        self,
        gmail_adapter: GmailAdapter,
        drive_adapter: GoogleDriveAdapter,
        notion_adapter: NotionAdapter
    ):
        self.gmail_adapter = gmail_adapter
        self.drive_adapter = drive_adapter
        self.notion_adapter = notion_adapter
        self.mail_perso = os.getenv('MAIL_PERSO')

    def execute(self, lease: Lease):
        """
        Send the receipt (quittance) to the tenant if conditions are met.
        """
        tenant = lease.tenant
        prop = lease.property
        
        # 1. Validation
        if not lease.id:
            print(f"[ERROR] Lease ID missing for {tenant.full_name}")
            return
        if not prop or not prop.id:
            print(f"[ERROR] Property information missing for {tenant.full_name}")
            return
        
        # Check logic: only if EnvoiQuittanceResult is 'Reinit'
        # NotionAdapter maps this to tenant.statut_envoi_quittance
        if tenant.statut_envoi_quittance != 'Reinit':
            return 
            
        print(f"[INFO] Envoi quittance requis pour {tenant.full_name}")
        
        # 2. Prepare Data
        current_date = datetime.now()
        current_year = current_date.strftime('%Y')
        current_month_num = current_date.strftime('%m')
        
        # Formatted name logic - currently in naming.py expecting dict, but implementation provided only takes dict?
        # naming.py `build_formatted_name(locataire)` takes locataire dict.
        # I need to implement formatted name logic for Entity.
        # Logic: Upper/Title, remove spaces/accents/commas
        formatted_name = tenant.full_name.title().replace(" ", "_").replace("'", "_").replace(",", "")
        
        pattern = get_quittance_pattern(current_month_num, current_year, formatted_name)
        
        # 3. Find File in Drive
        # Need repo ID from property ID
        repo_id = MAP_PAGE_NOTION_BIEN_TO_REPO.get(prop.id)
        if not repo_id:
            self._handle_error(lease.id, tenant.full_name, f"Repo ID not found for property {prop.id} ({prop.address})")
            return
            
        # Traverse folders: Repo -> Year -> Recettes -> AT
        try:
            year_folder = self.drive_adapter.get_or_create_subfolder(repo_id, current_year) # Assuming repo has year folders
            # Logic in old code: `get_or_create_year_folder` which checks name=year.
            # My `get_or_create_subfolder` checks name.
            
            recettes_folder = self.drive_adapter.get_or_create_subfolder(year_folder, "Recettes")
            at_folder = self.drive_adapter.get_or_create_subfolder(recettes_folder, "AT")
            
            # Search file
            file_match = self.drive_adapter.find_receipt_in_folder(at_folder, pattern)
            
            if not file_match:
                self._handle_error(lease.id, tenant.full_name, f"Aucun fichier trouvé pour {formatted_name} en {current_month_num}/{current_year}")
                return
                
            # 4. Download and Send
            print(f"✅ Fichier trouvé : {file_match['name']}")
            file_content = self.drive_adapter.download_file(file_match['id'])
            
            sent = self.gmail_adapter.send_email_with_attachment(
                to_address=tenant.email,
                subject=f'Quittance de loyer {current_month_num} {current_year} {tenant.full_name}',
                body='Veuillez trouver ci-joint votre quittance de loyer.\n\nBien à vous,\nGuilhem Gerbault',
                attachment_name=file_match['name'],
                attachment_data=file_content
            )
            
            if sent:
                self.notion_adapter.update_lease_status(lease.id, QUITTANCE_RESULT_IDS["QuittanceSuccess"])
                print("📌 Statut mis à jour : Success")
            else:
                self.notion_adapter.update_lease_status(lease.id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
                print("📌 Statut mis à jour : Failure")
                
        except Exception as e:
            self._handle_error(lease.id, tenant.full_name, str(e))

    def _handle_error(self, lease_id: str, tenant_name: str, error_msg: str):
        print(f"🚫 Erreur pour {tenant_name}: {error_msg}")
        if self.mail_perso:
            self.gmail_adapter.send_email_with_attachment(
                to_address=self.mail_perso,
                subject=f"[ERREUR] Quittance {tenant_name}",
                body=f"Détails: {error_msg}",
                attachment_name="",
                attachment_data=None
            )
        self.notion_adapter.update_lease_status(lease_id, QUITTANCE_RESULT_IDS["QuittanceFailure"])
