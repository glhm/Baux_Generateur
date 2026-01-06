"""
Pytest configuration for E2E tests.
Provides fixtures for mocking external API calls.
"""
import pytest
from unittest.mock import patch, MagicMock

from tests.e2e.fixtures.mock_notion_responses import (
    get_mock_all_data_physique,
    get_mock_all_data_visale,
)
from tests.e2e.fixtures.mock_google_services import create_mock_google_services


@pytest.fixture
def mock_google_services():
    """Fixture providing mocked Google services."""
    return create_mock_google_services()


@pytest.fixture
def mock_notion_data_physique():
    """Fixture providing mock Notion data for physical guarantor case."""
    return get_mock_all_data_physique()


@pytest.fixture
def mock_notion_data_visale():
    """Fixture providing mock Notion data for Visale guarantor case."""
    return get_mock_all_data_visale()


@pytest.fixture
def patch_notion_api(mock_notion_data_physique):
    """
    Fixture that patches Notion API calls.
    Returns the mock data being used.
    """
    with patch('src.services.notion_service.requests.post') as mock_post:
        # Configure mock to return appropriate data based on database
        def mock_notion_response(url, **kwargs):
            response = MagicMock()
            response.json.return_value = {"results": []}
            
            # Extract database ID from URL
            if "databases" in url:
                if "753e298c" in url:  # locataire
                    response.json.return_value = mock_notion_data_physique["locataire"]
                elif "a2cc6287" in url:  # bien
                    response.json.return_value = mock_notion_data_physique["bien"]
                elif "1d87115f" in url:  # chambres
                    response.json.return_value = mock_notion_data_physique["chambres"]
                elif "a3f2eaf4" in url:  # garants
                    response.json.return_value = mock_notion_data_physique["garants"]
                elif "19bcaf23" in url:  # loyer
                    response.json.return_value = mock_notion_data_physique["loyer"]
            
            return response
        
        mock_post.side_effect = mock_notion_response
        yield mock_post


@pytest.fixture
def patch_google_services(mock_google_services):
    """
    Fixture that patches Google API authentication and services.
    Returns the mock services for assertions.
    """
    with patch('src.services.google_doc_and_drive_service.authenticate_and_create_services') as mock_auth:
        mock_auth.return_value = (
            mock_google_services.drive_service,
            mock_google_services.docs_service,
            mock_google_services.gmail_service
        )
        yield mock_google_services


@pytest.fixture
def patch_create_doc(mock_google_services):
    """
    Fixture that patches create_and_export_doc_from_template.
    Tracks all document creation calls.
    """
    with patch('src.use_cases.generate_lease_use_case.create_and_export_doc_from_template') as mock_create:
        def track_creation(template_id, new_document_name, replace_requests, folder_id, drive_service, docs_service):
            mock_google_services.record_document_creation(
                template_id, new_document_name, replace_requests, folder_id
            )
            return {"documentId": "mock-doc-id"}
        
        mock_create.side_effect = track_creation
        yield mock_google_services
