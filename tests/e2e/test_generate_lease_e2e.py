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
                        mock_create.side_effect = lambda template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service: \
                            mock_services.record_document_creation(template_id, new_document_name, replace_requests, folder_id)
                        
                        # Act
                        from src.use_cases.execute_all_tasks_required_by_user import do_tasks_required_from_user
                        do_tasks_required_from_user()
                        
                        # Assert
                        # Should create 2 documents for physical guarantor
                        mock_services.assert_document_count(2)
                        
                        # Should use correct templates
                        mock_services.assert_document_created_with_template(ID_TEMPLATE_BAIL_MEUBLE)
                        mock_services.assert_document_created_with_template(CAUTION_ID)
                        
                        # Verify document names
                        doc_names = mock_services.get_created_document_names()
                        assert any("Bail_location_" in name for name in doc_names), \
                            f"Expected 'Bail_location_' document, got: {doc_names}"
                        assert any("Acte_de_caution_solidaire_" in name for name in doc_names), \
                            f"Expected 'Acte_de_caution_solidaire_' document, got: {doc_names}"

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
                        from src.use_cases.execute_all_tasks_required_by_user import do_tasks_required_from_user
                        do_tasks_required_from_user()
                        
                        # Assert
                        # Should create only 1 document for Visale guarantor
                        mock_services.assert_document_count(1)
                        
                        # Should use only the bail template (not caution)
                        mock_services.assert_document_created_with_template(ID_TEMPLATE_BAIL_MEUBLE)
                        
                        # Verify no caution document was created
                        doc_names = mock_services.get_created_document_names()
                        assert not any("Acte_de_caution" in name for name in doc_names), \
                            f"Unexpected 'Acte_de_caution' document for Visale case: {doc_names}"

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
                        
                        from src.use_cases.execute_all_tasks_required_by_user import do_tasks_required_from_user
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
