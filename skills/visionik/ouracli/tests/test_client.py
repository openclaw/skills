"""Tests for client module."""

from unittest.mock import Mock, patch

from ouracli.client import OuraClient


class TestOuraClient:
    """Tests for OuraClient class."""

    @patch("ouracli.client.requests.Session")
    def test_init_with_token(self, mock_session: Mock) -> None:
        """Test initialization with provided token."""
        client = OuraClient(access_token="test_token")
        assert client.access_token == "test_token"

    @patch("ouracli.client.load_dotenv")
    @patch("ouracli.client.os.getenv", return_value="env_token")
    @patch("ouracli.client.Path")
    def test_load_token_from_env(
        self, mock_path: Mock, mock_getenv: Mock, mock_load_dotenv: Mock
    ) -> None:
        """Test loading token from environment file."""
        mock_path.cwd.return_value = mock_path
        mock_path.__truediv__.return_value = mock_path
        mock_path.exists.return_value = True

        client = OuraClient()
        assert client.access_token == "env_token"

    @patch("ouracli.client.requests.Session")
    def test_get_daily_activity(self, mock_session: Mock) -> None:
        """Test getting daily activity data."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": "1"}]}
        mock_session.return_value.get.return_value = mock_response

        client = OuraClient(access_token="test_token")
        result = client.get_daily_activity("2024-01-01", "2024-01-07")

        assert "data" in result
        assert len(result["data"]) == 1

    @patch("ouracli.client.requests.Session")
    def test_get_personal_info(self, mock_session: Mock) -> None:
        """Test getting personal info."""
        mock_response = Mock()
        mock_response.json.return_value = {"age": 30, "weight": 70}
        mock_session.return_value.get.return_value = mock_response

        client = OuraClient(access_token="test_token")
        result = client.get_personal_info()

        assert "age" in result
        assert result["age"] == 30

    @patch("ouracli.client.requests.Session")
    def test_get_all_data(self, mock_session: Mock) -> None:
        """Test getting all data."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_session.return_value.get.return_value = mock_response

        client = OuraClient(access_token="test_token")
        result = client.get_all_data("2024-01-01", "2024-01-07")

        assert isinstance(result, dict)
        assert "activity" in result
        assert "sleep" in result
        assert "readiness" in result
