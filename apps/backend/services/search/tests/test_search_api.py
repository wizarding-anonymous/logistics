from fastapi.testclient import TestClient
from unittest.mock import patch

def test_search_endpoint(client: TestClient):
    """
    Test the /search endpoint, mocking the service call.
    """
    mock_search_results = [
        {"id": "123", "description": "An order for widgets"},
        {"id": "456", "name": "A supplier"}
    ]

    # Use patch to replace the service function with a mock
    with patch('search.service.search_documents', return_value=mock_search_results) as mock_search:
        response = client.get("/?q=test")

        assert response.status_code == 200
        assert response.json() == mock_search_results

        # Verify that our service function was called with the correct query
        mock_search.assert_called_once_with(query="test")
