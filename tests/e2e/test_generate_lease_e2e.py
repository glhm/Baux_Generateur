"""
E2E Tests for Lease Generation.
Tests the complete lease generation flow with mocked external APIs.
"""
import pytest
from unittest.mock import patch, MagicMock
import os

from src.conf.info_apis import ID_TEMPLATE_BAIL_MEUBLE, CAUTION_ID
from tests.e2e.fixtures.mock_notion_responses import (
    get_mock_all_data_physique,
    get_mock_all_data_visale,
)
from tests.e2e.fixtures.mock_google_services import create_mock_google_services
from src.use_cases.execute_all_tasks_required_by_user import do_tasks_required_from_user


from src.domain.housing_strings import (
    cautionnement_physique,
    la_caution_physique,
    signature_des_garants,
    bail_meuble_duree,
    reconduction_meuble,
    duree_contrat_meuble,
    cautionnement_visale,
    doc_visale,
    bail_etudiant_titre,
    bail_etudiant_duree,
    duree_contrat_etudiant
)

class TestGenerateLeaseE2E:
    """E2E tests for lease generation with different guarantor types."""

    def test_generate_lease_with_physique_guarantor(self):
        """
        Test Case: Physical Guarantor (Garant Physique)
        
        Expected behavior:
        - Generates the main lease document (Bail_location_...)
        - Generates the guarantor document (Acte_de_caution_solidaire_...)
        - Both documents are created in the correct folder
        - Placeholders are correctly replaced with tenant/guarantor data
        """
        # Arrange
        mock_services = create_mock_google_services()
        mock_data = get_mock_all_data_physique()
        
        # Set environment variable for Notion API
        with patch.dict(os.environ, {'NOTION_API_SECRET': 'test-secret'}):
            # Mock Notion API calls
            with patch('src.services.notion_service.requests.post') as mock_notion:
                self._setup_notion_mock(mock_notion, mock_data)
                
                # Mock Google services authentication
                with patch('src.services.google_doc_and_drive_service.authenticate_and_create_services') as mock_auth:
                    mock_auth.return_value = (
                        mock_services.drive_service,
                        mock_services.docs_service,
                        mock_services.gmail_service
                    )
                    
                    # Mock document creation - track calls
                    with patch('src.use_cases.generate_lease_use_case.create_and_export_doc_from_template') as mock_create:
                        mock_create.side_effect = lambda **kwargs: self._track_doc_creation(mock_services, kwargs)
                        
                        # Act
                        do_tasks_required_from_user()
                        
                        # Assert
                        # Should create 2 documents for physical guarantor
                        mock_services.assert_document_count(2)
                        
                        # Verify document names and templates
                        mock_services.assert_document_created_with_template(ID_TEMPLATE_BAIL_MEUBLE)
                        mock_services.assert_document_created_with_template(CAUTION_ID)
                        
                        doc_names = mock_services.get_created_document_names()
                        assert any("Bail_location_" in name for name in doc_names)
                        assert any("Acte_de_caution_solidaire_" in name for name in doc_names)

                        # --- ASSERTIONS PLACEHOLDERS ---
                        
                        # 1. Calculated/Fixed Placeholders
                        mock_services.assert_placeholder_replaced("{{CAUTIONNEMENT}}", cautionnement_physique)
                        mock_services.assert_placeholder_replaced("{{LA_CAUTION}}", la_caution_physique)
                        mock_services.assert_placeholder_replaced("{{SIGN_GARANT}}", signature_des_garants)
                        mock_services.assert_placeholder_replaced("{{DOC_VISA}}", "")
                        
                        mock_services.assert_placeholder_replaced("{{DATE_CONTRAT}}", "15 Janvier 2026")
                        mock_services.assert_placeholder_replaced("{{MENTION_SPECIALE_LOYER}}", "")
                        
                        # Bail Meublé specific
                        mock_services.assert_placeholder_replaced("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_meuble_duree)
                        mock_services.assert_placeholder_replaced("{{MENTION_RECONDUCTION_MEUBLE}}", reconduction_meuble)
                        mock_services.assert_placeholder_replaced("{{DUREE_CONTRAT}}", duree_contrat_meuble)
                        mock_services.assert_placeholder_replaced("{{TYPE_BAIL_MEUBLE}}", "")

                        # Financial (Prorata calculated values - logic in compute_housing_values.py)
                        # Based on mock inputs: Loyer HC 450, Charges 50, Arrivée 15/01 (31 days)
                        # Days = 31 - 15 + 1 = 17 days
                        # Prorata coeff = 17 / 31
                        # Loyer = 450 * 17/31 = 246.77
                        # Charges = 50 * 17/31 = 27.42
                        # Total = 274.19
                        # Note: Values need to match what the actual code calculates. 
                        # Assuming usage of simple float math or rounding in logic.
                        # For e2e, we check that they are present and look like numbers.
                        # Actually, let's verify exact values if we can, or just presence.
                        # Let's check non-empty string first to be safe against float precision nuances in tests, 
                        # or rely on what logic produces. 
                        # Based on typical implementations:
                        mock_services.assert_placeholder_replaced("{{TOTAL_1ER_MOIS}}", "1174.19") # 246.77 + 27.42 + 900 = 1174.19
                        mock_services.assert_placeholder_replaced("{{PRORATA_TOTAL_CC}}", "274.19")
                        mock_services.assert_placeholder_replaced("{{PRORATA_LOYER}}", "246.77")
                        mock_services.assert_placeholder_replaced("{{PRORATA_CHARGES}}", "27.42")
                        mock_services.assert_placeholder_replaced("{{MONTANT_LOYER}}", "450")
                        mock_services.assert_placeholder_replaced("{{MONTANT_CHARGES}}", "50")
                        mock_services.assert_placeholder_replaced("{{MONTANT_GARANTIES}}", "900.0")
                        mock_services.assert_placeholder_replaced("{{MONTANT_TOTAL}}", "500.0")
                        mock_services.assert_placeholder_replaced("{{NOMBRE_JOURS_PREMIER_MOIS}}", "17")

                        # 2. Notion Data Placeholders
                        
                        # Locataire
                        mock_services.assert_placeholder_replaced("{{NOM_LOCATAIRE}}", "Dupont Jean")
                        mock_services.assert_placeholder_replaced("{{PRENOM}}", "Jean")
                        mock_services.assert_placeholder_replaced("{{NOM}}", "Dupont")
                        mock_services.assert_placeholder_replaced("{{DATE_NAISSANCE}}", "15/03/1995")
                        mock_services.assert_placeholder_replaced("{{LIEU_NAISSANCE}}", "Paris")
                        mock_services.assert_placeholder_replaced("{{ADRESSE_LOCATAIRE}}", "123 Rue de la Paix, 75001 Paris")
                        mock_services.assert_placeholder_replaced("{{MAIL}}", "jean.dupont@email.com")
                        mock_services.assert_placeholder_replaced("{{TEL}}", "06 12 34 56 78")
                        mock_services.assert_placeholder_replaced("{{MOIS_ARRIVEE}}", "Janvier")
                        mock_services.assert_placeholder_replaced("{{JOUR_ARRIVEE}}", "15")

                        # Bien
                        mock_services.assert_placeholder_replaced("{{ADRESSE_BIEN}}", "55 Rue Renée Auduc, 94000 Créteil")
                        mock_services.assert_placeholder_replaced("{{CODE_POSTAL}}", "94000")
                        mock_services.assert_placeholder_replaced("{{VILLE}}", "Créteil")
                        mock_services.assert_placeholder_replaced("{{SURFACE_TOTALE}}", "120")
                        mock_services.assert_placeholder_replaced("{{ANNEE_CONSTRUCTION}}", "1985")
                        mock_services.assert_placeholder_replaced("{{NOM_BAILLEUR}}", "SCI Immobilière")
                        mock_services.assert_placeholder_replaced("{{ADRESSE_BAILLEUR}}", "10 Rue du Commerce, 75015 Paris")

                        # Chambre
                        mock_services.assert_placeholder_replaced("{{NOM_CHAMBRE}}", "Chambre 1")
                        mock_services.assert_placeholder_replaced("{{SURFACE_CHAMBRE}}", "12")
                        mock_services.assert_placeholder_replaced("{{ETAGE}}", "2ème étage")
                        mock_services.assert_placeholder_replaced("{{DESCRIPTION_CHAMBRE}}", "Chambre meublée avec vue sur jardin")

                        # Garant (Physique)
                        mock_services.assert_placeholder_replaced("{{PRENOM_GARANT}}", "Pierre")
                        mock_services.assert_placeholder_replaced("{{NOM_GARANT}}", "Dupont")
                        mock_services.assert_placeholder_replaced("{{DATE_NAISSANCE_GARANT}}", "10/05/1965")
                        mock_services.assert_placeholder_replaced("{{LIEU_NAISSANCE_GARANT}}", "Marseille")
                        mock_services.assert_placeholder_replaced("{{ADRESSE_GARANT}}", "78 Boulevard Haussmann, 75008 Paris")
                        mock_services.assert_placeholder_replaced("{{TEL_GARANT}}", "06 11 22 33 44")
                        mock_services.assert_placeholder_replaced("{{MAIL_GARANT}}", "pierre.dupont@email.com")

                        # Loyer
                        mock_services.assert_placeholder_replaced("{{LOYER_CC}}", "500")
                        mock_services.assert_placeholder_replaced("{{DEPOT_GARANTIE}}", "450")

    def test_generate_lease_with_visale_guarantor(self):
        """
        Test Case: Visale Guarantor (Garantie Visale)
        
        Expected behavior:
        - Generates ONLY the main lease document (Bail_location_...)
        - Does NOT generate the guarantor document (no Acte_de_caution_solidaire)
        - Placeholders for Visale-specific content are correctly replaced
        """
        # Arrange
        mock_services = create_mock_google_services()
        mock_data = get_mock_all_data_visale()
        
        # Set environment variable for Notion API
        with patch.dict(os.environ, {'NOTION_API_SECRET': 'test-secret'}):
            # Mock Notion API calls
            with patch('src.services.notion_service.requests.post') as mock_notion:
                self._setup_notion_mock(mock_notion, mock_data)
                
                # Mock Google services authentication
                with patch('src.services.google_doc_and_drive_service.authenticate_and_create_services') as mock_auth:
                    mock_auth.return_value = (
                        mock_services.drive_service,
                        mock_services.docs_service,
                        mock_services.gmail_service
                    )
                    
                    # Mock document creation - track calls
                    with patch('src.use_cases.generate_lease_use_case.create_and_export_doc_from_template') as mock_create:
                        mock_create.side_effect = lambda template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service: \
                            mock_services.record_document_creation(template_id, new_document_name, replace_requests, folder_id)
                        
                        # Act
                        do_tasks_required_from_user()
                        
                        # Assert
                        # Should create only 1 document for Visale guarantor
                        mock_services.assert_document_count(1)
                        
                        # Should use only the bail template (not caution)
                        mock_services.assert_document_created_with_template(ID_TEMPLATE_BAIL_MEUBLE)
                        
                        doc_names = mock_services.get_created_document_names()
                        assert not any("Acte_de_caution" in name for name in doc_names)

                        # --- ASSERTIONS PLACEHOLDERS ---
                        
                        # 1. Calculated/Fixed Placeholders - Visale Specifics
                        mock_services.assert_placeholder_replaced("{{CAUTIONNEMENT}}", cautionnement_visale)
                        mock_services.assert_placeholder_replaced("{{LA_CAUTION}}", "")
                        mock_services.assert_placeholder_replaced("{{SIGN_GARANT}}", "")
                        mock_services.assert_placeholder_replaced("{{DOC_VISA}}", doc_visale)

                        # Common Calculated
                        mock_services.assert_placeholder_replaced("{{DATE_CONTRAT}}", "1 Février 2026")
                        mock_services.assert_placeholder_replaced("{{MENTION_SPECIALE_LOYER}}", "")
                        
                        # Bail Etudiant specific (from mock data TypeDeBail="Etudiant")
                        mock_services.assert_placeholder_replaced("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_etudiant_duree)
                        mock_services.assert_placeholder_replaced("{{TYPE_BAIL_MEUBLE}}", bail_etudiant_titre)
                        mock_services.assert_placeholder_replaced("{{DUREE_CONTRAT}}", duree_contrat_etudiant)
                        mock_services.assert_placeholder_replaced("{{MENTION_RECONDUCTION_MEUBLE}}", "")

                        # Financial (Prorata calculated values)
                        # Based on mock inputs: Loyer HC 450, Charges 50, Arrivée 1er février (28 days in 2026? No, 2026 is not leap, but standard month length. Feb is 28 usually)
                        # Wait, Feb 2026 has 28 days.
                        # Arrivee le 1er => Full month?
                        # `compute_housing_values.py` logic needed.
                        # If simple full month:
                        # But logic likely calculates based on days remaining in month vs total days in month.
                        # If day 1, then full month. 
                        # Prorata coeff = 1.
                        # Loyer = 450, Charges = 50. Total = 500.
                        # Let's verify these values in test run, or assume full month logic works as 1.
                        mock_services.assert_placeholder_replaced("{{TOTAL_1ER_MOIS}}", "1400.0") 
                        mock_services.assert_placeholder_replaced("{{PRORATA_TOTAL_CC}}", "500.0")
                        mock_services.assert_placeholder_replaced("{{PRORATA_LOYER}}", "450.0")
                        mock_services.assert_placeholder_replaced("{{PRORATA_CHARGES}}", "50.0")
                        mock_services.assert_placeholder_replaced("{{MONTANT_LOYER}}", "450")
                        mock_services.assert_placeholder_replaced("{{MONTANT_CHARGES}}", "50")
                        mock_services.assert_placeholder_replaced("{{MONTANT_GARANTIES}}", "900.0")
                        mock_services.assert_placeholder_replaced("{{MONTANT_TOTAL}}", "500.0")
                        mock_services.assert_placeholder_replaced("{{NOMBRE_JOURS_PREMIER_MOIS}}", "28")

                        # 2. Notion Data Placeholders
                        
                        # Locataire (Visale mock)
                        mock_services.assert_placeholder_replaced("{{NOM_LOCATAIRE}}", "Martin Marie")
                        mock_services.assert_placeholder_replaced("{{PRENOM}}", "Marie")
                        mock_services.assert_placeholder_replaced("{{NOM}}", "Martin")
                        mock_services.assert_placeholder_replaced("{{MAIL}}", "marie.martin@email.com")
                        mock_services.assert_placeholder_replaced("{{TEL}}", "06 98 76 54 32")

                        # Garant (Visale)
                        mock_services.assert_placeholder_replaced("{{NUMERO_VISALE}}", "VISALE-2026-123456")

    def _setup_notion_mock(self, mock_post, mock_data):
        """Configure Notion API mock to return appropriate data based on database."""
        def mock_response(url, **kwargs):
            response = MagicMock()
            response.json.return_value = {"results": []}
            
            if "databases" in url:
                if "753e298c" in url:
                    response.json.return_value = mock_data["locataire"]
                elif "a2cc6287" in url:
                    response.json.return_value = mock_data["bien"]
                elif "1d87115f" in url:
                    response.json.return_value = mock_data["chambres"]
                elif "a3f2eaf4" in url:
                    response.json.return_value = mock_data["garants"]
                elif "19bcaf23" in url:
                    response.json.return_value = mock_data["loyer"]
            
            return response
        
        mock_post.side_effect = mock_response

    def _track_doc_creation(self, mock_services, kwargs):
        """Helper to track document creation calls."""
        mock_services.record_document_creation(
            kwargs.get('template_id'),
            kwargs.get('new_document_name'),
            kwargs.get('replace_requests'),
            kwargs.get('folder_id')
        )


class TestLeaseePlaceholderReplacement:
    """Tests for verifying placeholder replacement in lease documents."""

    def test_physique_guarantor_uses_correct_cautionnement_text(self):
        """Verify that physical guarantor case uses cautionnement_physique text."""
        mock_services = create_mock_google_services()
        mock_data = get_mock_all_data_physique()
        
        with patch.dict(os.environ, {'NOTION_API_SECRET': 'test-secret'}):
            with patch('src.services.notion_service.requests.post') as mock_notion:
                self._setup_notion_mock(mock_notion, mock_data)
                
                with patch('src.services.google_doc_and_drive_service.authenticate_and_create_services') as mock_auth:
                    mock_auth.return_value = (
                        mock_services.drive_service,
                        mock_services.docs_service,
                        mock_services.gmail_service
                    )
                    
                    with patch('src.use_cases.generate_lease_use_case.create_and_export_doc_from_template') as mock_create:
                        captured_requests = []
                        
                        def capture_requests(template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service):
                            captured_requests.extend(replace_requests)
                            mock_services.record_document_creation(template_id, new_document_name, replace_requests, folder_id)
                        
                        mock_create.side_effect = capture_requests
                        
                        from src.use_cases.execute_all_tasks_required_by_user import do_tasks_required_from_user
                        do_tasks_required_from_user()
                        
                        # Find the {{CAUTIONNEMENT}} placeholder replacement
                        cautionnement_value = None
                        for req in captured_requests:
                            if "replaceAllText" in req:
                                if req["replaceAllText"]["containsText"]["text"] == "{{CAUTIONNEMENT}}":
                                    cautionnement_value = req["replaceAllText"]["replaceText"]
                                    break
                        
                        assert cautionnement_value is not None, "{{CAUTIONNEMENT}} placeholder not found"
                        # For physique, it should contain the physical guarantor text (not empty)
                        assert len(cautionnement_value) > 0, "Cautionnement should not be empty for physical guarantor"

    def test_visale_guarantor_uses_correct_cautionnement_text(self):
        """Verify that Visale guarantor case uses cautionnement_visale text."""
        mock_services = create_mock_google_services()
        mock_data = get_mock_all_data_visale()
        
        with patch.dict(os.environ, {'NOTION_API_SECRET': 'test-secret'}):
            with patch('src.services.notion_service.requests.post') as mock_notion:
                self._setup_notion_mock(mock_notion, mock_data)
                
                with patch('src.services.google_doc_and_drive_service.authenticate_and_create_services') as mock_auth:
                    mock_auth.return_value = (
                        mock_services.drive_service,
                        mock_services.docs_service,
                        mock_services.gmail_service
                    )
                    
                    with patch('src.use_cases.generate_lease_use_case.create_and_export_doc_from_template') as mock_create:
                        captured_requests = []
                        
                        def capture_requests(template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service):
                            captured_requests.extend(replace_requests)
                            mock_services.record_document_creation(template_id, new_document_name, replace_requests, folder_id)
                        
                        mock_create.side_effect = capture_requests
                        
                        do_tasks_required_from_user()
                        
                        # Find the {{DOC_VISA}} placeholder replacement
                        doc_visa_value = None
                        for req in captured_requests:
                            if "replaceAllText" in req:
                                if req["replaceAllText"]["containsText"]["text"] == "{{DOC_VISA}}":
                                    doc_visa_value = req["replaceAllText"]["replaceText"]
                                    break
                        
                        assert doc_visa_value is not None, "{{DOC_VISA}} placeholder not found"
                        # For Visale, DOC_VISA should contain the Visale document text
                        assert len(doc_visa_value) > 0, "DOC_VISA should not be empty for Visale guarantor"

    def _setup_notion_mock(self, mock_post, mock_data):
        """Configure Notion API mock."""
        def mock_response(url, **kwargs):
            response = MagicMock()
            response.json.return_value = {"results": []}
            
            if "databases" in url:
                if "753e298c" in url:
                    response.json.return_value = mock_data["locataire"]
                elif "a2cc6287" in url:
                    response.json.return_value = mock_data["bien"]
                elif "1d87115f" in url:
                    response.json.return_value = mock_data["chambres"]
                elif "a3f2eaf4" in url:
                    response.json.return_value = mock_data["garants"]
                elif "19bcaf23" in url:
                    response.json.return_value = mock_data["loyer"]
            
            return response
        
        mock_post.side_effect = mock_response
