"""
Tests for Linear API client
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api.linear_client import LinearClient, LinearAPIError
from src.utils.auth import validate_api_key


class TestLinearClient:
    """Tests for LinearClient class"""

    def test_init(self):
        """Test LinearClient initialization"""
        client = LinearClient()
        assert client.api_url is not None
        assert client.headers is not None
        assert client.request_count == 0

    @patch('src.api.linear_client.requests.post')
    def test_execute_query_success(self, mock_post):
        """Test successful query execution"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {"id": "test-id", "name": "Test User"}
            }
        }
        mock_post.return_value = mock_response

        client = LinearClient()
        result = client._execute_query("query { viewer { id name } }")

        assert "viewer" in result
        assert result["viewer"]["id"] == "test-id"
        assert client.request_count == 1

    @patch('src.api.linear_client.requests.post')
    def test_execute_query_with_errors(self, mock_post):
        """Test query execution with GraphQL errors"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "Test error"}]
        }
        mock_post.return_value = mock_response

        client = LinearClient()

        with pytest.raises(LinearAPIError) as exc_info:
            client._execute_query("query { invalid }")

        assert "Test error" in str(exc_info.value)

    @patch('src.api.linear_client.requests.post')
    def test_execute_query_rate_limited(self, mock_post):
        """Test rate limit handling"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_post.return_value = mock_response

        client = LinearClient()

        with pytest.raises(LinearAPIError) as exc_info:
            client._execute_query("query { viewer { id } }")

        assert "Rate limited" in str(exc_info.value)

    @patch('src.api.linear_client.requests.post')
    def test_get_viewer(self, mock_post):
        """Test getting viewer information"""
        # Mock successful viewer response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "id": "viewer-123",
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
        }
        mock_post.return_value = mock_response

        client = LinearClient()
        viewer = client.get_viewer()

        assert viewer is not None
        assert viewer["id"] == "viewer-123"
        assert viewer["name"] == "Test User"

    @patch('src.api.linear_client.requests.post')
    def test_get_projects(self, mock_post):
        """Test fetching projects"""
        # Mock projects response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "projects": {
                    "nodes": [
                        {
                            "id": "project-1",
                            "name": "Test Project",
                            "state": "started"
                        }
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        client = LinearClient()
        projects = client.get_projects()

        assert len(projects) == 1
        assert projects[0]["id"] == "project-1"
        assert projects[0]["name"] == "Test Project"


class TestAuth:
    """Tests for authentication utilities"""

    @patch('src.utils.auth.requests.post')
    def test_validate_api_key_valid(self, mock_post):
        """Test API key validation with valid key"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {"id": "test-id", "name": "Test User"}
            }
        }
        mock_post.return_value = mock_response

        is_valid, message = validate_api_key("valid-key")

        assert is_valid is True
        assert "valid" in message.lower()

    @patch('src.utils.auth.requests.post')
    def test_validate_api_key_invalid(self, mock_post):
        """Test API key validation with invalid key"""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        is_valid, message = validate_api_key("invalid-key")

        assert is_valid is False
        assert "unauthorized" in message.lower() or "invalid" in message.lower()

    def test_validate_api_key_empty(self):
        """Test API key validation with empty key"""
        is_valid, message = validate_api_key("")

        assert is_valid is False
        assert "empty" in message.lower()
