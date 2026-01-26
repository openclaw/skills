"""Tests to boost coverage to 90% by covering previously untested code paths."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from ouracli.client import OuraClient
from ouracli.format_html import format_html
from ouracli.format_markdown import format_markdown
from ouracli.format_tree import format_tree
from ouracli.format_utils import reorganize_by_day
from ouracli.llm_help import show_llm_help


class TestLLMHelp:
    """Test LLM help documentation."""

    def test_show_llm_help_returns_string(self) -> None:
        """Test that show_llm_help returns documentation string."""
        result = show_llm_help()
        assert isinstance(result, str)
        assert len(result) > 1000  # Should be comprehensive
        assert "ouracli" in result.lower()
        assert "date" in result.lower()


class TestOuraClientTokenLoading:
    """Test OuraClient token loading from various sources."""

    def test_token_from_environment_variable(self) -> None:
        """Test loading token from environment variable."""
        with patch.dict(os.environ, {"PERSONAL_ACCESS_TOKEN": "test_token_123"}):
            client = OuraClient()
            assert client.access_token == "test_token_123"

    def test_token_from_local_secrets_file(self, tmp_path: Path) -> None:
        """Test loading token from local secrets/oura.env file."""
        # Create secrets directory
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "oura.env"
        secrets_file.write_text("PERSONAL_ACCESS_TOKEN=local_token_456\n")

        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                client = OuraClient()
                assert client.access_token == "local_token_456"

    def test_token_from_home_secrets_file(self, tmp_path: Path) -> None:
        """Test loading token from ~/.secrets/oura.env file."""
        # Create .secrets directory in tmp (simulating home)
        secrets_dir = tmp_path / ".secrets"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "oura.env"
        secrets_file.write_text("PERSONAL_ACCESS_TOKEN=home_token_789\n")

        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.cwd", return_value=Path("/nonexistent")):
                with patch("pathlib.Path.home", return_value=tmp_path):
                    client = OuraClient()
                    assert client.access_token == "home_token_789"

    def test_token_missing_exits(self, capsys: pytest.CaptureFixture) -> None:
        """Test that missing token causes sys.exit."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.cwd", return_value=Path("/nonexistent")):
                with patch("pathlib.Path.home", return_value=Path("/nonexistent")):
                    with pytest.raises(SystemExit) as exc_info:
                        OuraClient()
                    assert exc_info.value.code == 1
                    captured = capsys.readouterr()
                    assert "PERSONAL_ACCESS_TOKEN not found" in captured.err


class TestOuraClientErrorHandling:
    """Test OuraClient error handling in get_all_data."""

    @patch("ouracli.client.requests.Session")
    def test_get_all_data_handles_exceptions(self, mock_session: MagicMock) -> None:
        """Test that get_all_data handles exceptions gracefully."""
        # Mock session to raise exceptions
        mock_response = MagicMock()
        mock_response.json.side_effect = requests.RequestException("API Error")
        mock_response.raise_for_status.side_effect = requests.RequestException("API Error")
        mock_session.return_value.get.return_value = mock_response

        client = OuraClient(access_token="test_token")
        result = client.get_all_data("2025-01-01", "2025-01-07")

        # All data types should be empty lists due to exceptions
        assert result["activity"] == []
        assert result["sleep"] == []
        assert result["readiness"] == []
        assert result["spo2"] == []
        assert result["stress"] == []
        assert result["heartrate"] == []
        assert result["workouts"] == []
        assert result["sessions"] == []
        assert result["tags"] == []
        assert result["rest_mode"] == []
        assert result["personal_info"] == []


class TestFormatTreeEdgeCases:
    """Test format_tree edge cases."""

    def test_format_tree_with_empty_met_items(self) -> None:
        """Test format_tree with MET data but empty items."""
        data = {"met": {"items": [], "interval": 60}}
        result = format_tree(data)
        # Should skip empty items list
        assert "Activity Chart" not in result

    def test_format_tree_with_invalid_heartrate_timestamp(self) -> None:
        """Test format_tree with invalid heartrate timestamps."""
        data = {
            "heartrate": [
                {"timestamp": "invalid", "bpm": 70},
                {"timestamp": "2025-01-01T12:00:00Z", "bpm": 75},
            ]
        }
        result = format_tree(data)
        # Should skip invalid timestamp but process valid one
        assert "2025-01-01" in result

    def test_format_tree_with_heartrate_missing_timestamp(self) -> None:
        """Test format_tree with heartrate readings missing timestamp."""
        data = {"heartrate": [{"bpm": 70}, {"timestamp": "2025-01-01T12:00:00Z", "bpm": 75}]}
        result = format_tree(data)
        # Should skip entries without timestamp
        assert "2025-01-01" in result

    def test_format_tree_simple_list_values(self) -> None:
        """Test format_tree with simple list values."""
        data = [1, 2, 3, "test"]
        result = format_tree(data)
        assert "1" in result
        assert "test" in result

    def test_format_tree_scalar_value(self) -> None:
        """Test format_tree with scalar value."""
        result = format_tree("simple string")
        assert "simple string" in result

    def test_format_tree_list_heartrate_invalid_timestamps(self) -> None:
        """Test format_tree with list of heartrate having invalid timestamps."""
        data = [
            {"timestamp": "invalid-ts", "bpm": 60},
            {"timestamp": "2025-01-01T10:00:00Z", "bpm": 70},
        ]
        result = format_tree(data)
        # Should process valid timestamp
        assert "2025-01-01" in result


class TestFormatHTMLEdgeCases:
    """Test format_html edge cases."""

    def test_format_html_dict_with_all_lists(self) -> None:
        """Test format_html with dict containing all list values."""
        data = {"activity": [], "sleep": []}
        result = format_html(data)
        assert "<!DOCTYPE html>" in result
        assert "No data" in result

    def test_format_html_nested_dict_item(self) -> None:
        """Test format_html with nested dict items."""
        data = {"activity": [{"day": "2025-01-01", "contributors": {"score1": 85, "score2": 90}}]}
        result = format_html(data)
        assert "<!DOCTYPE html>" in result
        assert "2025-01-01" in result
        assert "Score1" in result or "Score2" in result

    def test_format_html_list_without_heartrate(self) -> None:
        """Test format_html with list that's not heartrate data."""
        data = [{"day": "2025-01-01", "score": 85}, {"day": "2025-01-02", "score": 90}]
        result = format_html(data, title="Test Data")
        assert "Test Data" in result
        assert "2025-01-01" in result
        assert "2025-01-02" in result

    def test_format_html_heartrate_invalid_timestamps(self) -> None:
        """Test format_html with heartrate data having invalid timestamps."""
        data = [
            {"timestamp": "invalid", "bpm": 60},
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": 70},
        ]
        result = format_html(data)
        assert "<!DOCTYPE html>" in result
        # Should process valid timestamp
        assert "2025-01-01" in result


class TestFormatMarkdownEdgeCases:
    """Test format_markdown edge cases."""

    def test_format_markdown_dict_with_all_lists_empty(self) -> None:
        """Test format_markdown with dict of empty lists."""
        data = {"activity": [], "sleep": []}
        result = format_markdown(data)
        assert "Activity" in result
        assert "No data" in result

    def test_format_markdown_list_simple_items(self) -> None:
        """Test format_markdown with list of simple items."""
        data = ["item1", "item2", "item3"]
        result = format_markdown(data)
        assert "- item1" in result
        assert "- item2" in result

    def test_format_markdown_empty_list(self) -> None:
        """Test format_markdown with empty list."""
        result = format_markdown([])
        assert "No data" in result

    def test_format_markdown_heartrate_invalid_timestamps(self) -> None:
        """Test format_markdown with heartrate data having invalid timestamps."""
        data = [
            {"timestamp": "invalid", "bpm": 60},
            {"timestamp": "2025-01-01T10:00:00Z", "bpm": 70},
        ]
        result = format_markdown(data, title="Heart Rate")
        assert "Heart Rate" in result
        assert "2025-01-01" in result

    def test_format_markdown_single_dict_data(self) -> None:
        """Test format_markdown with single dict (not a list)."""
        data = {"score": 85, "date": "2025-01-01"}
        result = format_markdown(data)
        assert "# Data" in result
        assert "85" in result


class TestFormatUtilsReorganizeByDay:
    """Test reorganize_by_day utility function."""

    def test_reorganize_by_day_basic(self) -> None:
        """Test basic reorganization by day."""
        data = {
            "activity": [
                {"day": "2025-01-01", "steps": 10000},
                {"day": "2025-01-02", "steps": 8000},
            ],
            "sleep": [
                {"day": "2025-01-01", "score": 85},
                {"day": "2025-01-02", "score": 90},
            ],
        }
        result = reorganize_by_day(data)
        assert "2025-01-01" in result
        assert "2025-01-02" in result
        assert result["2025-01-01"]["activity"]["steps"] == 10000
        assert result["2025-01-01"]["sleep"]["score"] == 85

    def test_reorganize_by_day_with_heartrate(self) -> None:
        """Test reorganizing heartrate time-series data by day."""
        data = {
            "heartrate": [
                {"timestamp": "2025-01-01T10:00:00Z", "bpm": 70},
                {"timestamp": "2025-01-01T11:00:00Z", "bpm": 75},
                {"timestamp": "2025-01-02T10:00:00Z", "bpm": 72},
            ]
        }
        result = reorganize_by_day(data)
        assert "2025-01-01" in result
        assert "2025-01-02" in result
        assert len(result["2025-01-01"]["heartrate"]) == 2
        assert len(result["2025-01-02"]["heartrate"]) == 1

    def test_reorganize_by_day_invalid_heartrate_timestamps(self) -> None:
        """Test reorganizing heartrate with invalid timestamps."""
        data = {
            "heartrate": [
                {"timestamp": "invalid", "bpm": 70},
                {"timestamp": "2025-01-01T10:00:00Z", "bpm": 75},
            ]
        }
        result = reorganize_by_day(data)
        # Should only have valid timestamp
        assert "2025-01-01" in result
        assert len(result["2025-01-01"]["heartrate"]) == 1

    def test_reorganize_by_day_non_list_item(self) -> None:
        """Test reorganizing with non-list items."""
        data = {"personal_info": {"age": 30, "weight": 70}, "activity": []}
        result = reorganize_by_day(data)
        # personal_info should be skipped as it's not a list
        assert result == {}

    def test_reorganize_by_day_no_day_field(self) -> None:
        """Test reorganizing items without day field."""
        data = {"activity": [{"steps": 10000}, {"steps": 8000}]}
        result = reorganize_by_day(data)
        # Should not add items without day field
        assert result == {}

    def test_reorganize_by_day_sorted_chronologically(self) -> None:
        """Test that result is sorted chronologically."""
        data = {
            "activity": [
                {"day": "2025-01-03", "steps": 9000},
                {"day": "2025-01-01", "steps": 10000},
                {"day": "2025-01-02", "steps": 8000},
            ]
        }
        result = reorganize_by_day(data)
        days = list(result.keys())
        assert days == ["2025-01-01", "2025-01-02", "2025-01-03"]
