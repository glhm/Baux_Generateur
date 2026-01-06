"""
Mock Google Drive and Docs services for E2E tests.
Provides mock implementations that track API calls for assertions.
"""
from unittest.mock import MagicMock


class MockGoogleServices:
    """Container for mocked Google services with call tracking."""
    
    def __init__(self):
        self.drive_service = MagicMock()
        self.docs_service = MagicMock()
        self.gmail_service = MagicMock()
        
        # Track calls to create_and_export_doc_from_template
        self.created_documents = []
        
        # Setup drive service mock responses
        self._setup_drive_mocks()
        self._setup_docs_mocks()
    
    def _setup_drive_mocks(self):
        """Configure Drive service mock responses."""
        # Mock file copy operation
        self.drive_service.files().copy().execute.return_value = {
            "id": "new-doc-id-12345",
            "name": "Mocked Document"
        }
        
        # Mock file list operation
        self.drive_service.files().list().execute.return_value = {
            "files": []
        }
        
        # Mock file delete operation
        self.drive_service.files().delete().execute.return_value = None
        
        # Mock file export (for PDF)
        self.drive_service.files().export_media.return_value = MagicMock()
        
        # Mock file create
        self.drive_service.files().create().execute.return_value = {
            "id": "uploaded-pdf-id-67890"
        }
    
    def _setup_docs_mocks(self):
        """Configure Docs service mock responses."""
        # Mock batchUpdate operation
        self.docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }
        
        # Mock document get
        self.docs_service.documents().get().execute.return_value = {
            "documentId": "doc-id-12345",
            "title": "Mocked Document"
        }
    
    def record_document_creation(self, template_id, document_name, replace_requests, folder_id):
        """Record a document creation call for later assertions."""
        self.created_documents.append({
            "template_id": template_id,
            "document_name": document_name,
            "replace_requests": replace_requests,
            "folder_id": folder_id
        })
    
    def get_created_document_names(self):
        """Return list of created document names."""
        return [doc["document_name"] for doc in self.created_documents]
    
    def get_document_count(self):
        """Return the number of documents created."""
        return len(self.created_documents)
    
    def assert_document_created_with_template(self, template_id):
        """Assert that a document was created using the specified template."""
        template_ids = [doc["template_id"] for doc in self.created_documents]
        assert template_id in template_ids, \
            f"Expected template {template_id} not found in created documents. Found: {template_ids}"
    
    def assert_document_count(self, expected_count):
        """Assert the expected number of documents were created."""
        actual_count = len(self.created_documents)
        assert actual_count == expected_count, \
            f"Expected {expected_count} documents, but {actual_count} were created"
    
    def assert_placeholder_replaced(self, placeholder, expected_value):
        """Assert that a placeholder was replaced with the expected value."""
        for doc in self.created_documents:
            for request in doc["replace_requests"]:
                if "replaceAllText" in request:
                    text = request["replaceAllText"]["containsText"]["text"]
                    if text == placeholder:
                        actual_value = request["replaceAllText"]["replaceText"]
                        assert actual_value == expected_value, \
                            f"Placeholder {placeholder}: expected '{expected_value}', got '{actual_value}'"
                        return
        raise AssertionError(f"Placeholder {placeholder} not found in any replace requests")


def create_mock_google_services():
    """Factory function to create mock Google services."""
    return MockGoogleServices()
