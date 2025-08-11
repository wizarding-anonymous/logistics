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
        mock_search.assert_called_once_with(query="test", status=None, min_price=None, max_price=None)

def test_search_endpoint_with_filters(client: TestClient):
    """
    Test the /search endpoint with filters, mocking the service call.
    """
    mock_search_results = [{"id": "789", "status": "closed"}]

    with patch('search.service.search_documents', return_value=mock_search_results) as mock_search:
        response = client.get("/?q=widgets&status=closed&min_price=100")

        assert response.status_code == 200
        assert response.json() == mock_search_results

        # Verify that our service function was called with all the correct arguments
        mock_search.assert_called_once_with(query="widgets", status="closed", min_price=100.0, max_price=None)
