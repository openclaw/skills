"""Tests for CLI module."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from ouracli.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    @patch("ouracli.cli.OuraClient")
    def test_activity_command(self, mock_client: Mock) -> None:
        """Test activity command."""
        mock_instance = Mock()
        mock_instance.get_daily_activity.return_value = {"data": [{"id": "1", "steps": 10000}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["activity", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_sleep_command(self, mock_client: Mock) -> None:
        """Test sleep command."""
        mock_instance = Mock()
        mock_instance.get_daily_sleep.return_value = {"data": [{"id": "1", "score": 85}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["sleep", "yesterday"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_readiness_command(self, mock_client: Mock) -> None:
        """Test readiness command."""
        mock_instance = Mock()
        mock_instance.get_daily_readiness.return_value = {"data": [{"id": "1", "score": 80}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["readiness", "7 days"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_spo2_command(self, mock_client: Mock) -> None:
        """Test spo2 command."""
        mock_instance = Mock()
        mock_instance.get_daily_spo2.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["spo2", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_stress_command(self, mock_client: Mock) -> None:
        """Test stress command."""
        mock_instance = Mock()
        mock_instance.get_daily_stress.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["stress", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_heartrate_command(self, mock_client: Mock) -> None:
        """Test heartrate command."""
        mock_instance = Mock()
        mock_instance.get_heartrate.return_value = {"data": [{"bpm": 60}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["heartrate", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_workout_command(self, mock_client: Mock) -> None:
        """Test workout command."""
        mock_instance = Mock()
        mock_instance.get_workouts.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["workout", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_session_command(self, mock_client: Mock) -> None:
        """Test session command."""
        mock_instance = Mock()
        mock_instance.get_sessions.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["session", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_tag_command(self, mock_client: Mock) -> None:
        """Test tag command."""
        mock_instance = Mock()
        mock_instance.get_tags.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["tag", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_rest_mode_command(self, mock_client: Mock) -> None:
        """Test rest_mode command."""
        mock_instance = Mock()
        mock_instance.get_rest_mode_periods.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["rest-mode", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_personal_info_command(self, mock_client: Mock) -> None:
        """Test personal_info command."""
        mock_instance = Mock()
        mock_instance.get_personal_info.return_value = {"age": 30}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["personal-info"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_all_command(self, mock_client: Mock) -> None:
        """Test all command."""
        mock_instance = Mock()
        mock_instance.get_all_data.return_value = {"activity": [], "sleep": []}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["all", "today"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_format_json(self, mock_client: Mock) -> None:
        """Test JSON format option."""
        mock_instance = Mock()
        mock_instance.get_daily_activity.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["activity", "today", "--json"])
        assert result.exit_code == 0
        assert '"id": "1"' in result.stdout

    @patch("ouracli.cli.OuraClient")
    def test_format_dataframe(self, mock_client: Mock) -> None:
        """Test dataframe format option."""
        mock_instance = Mock()
        mock_instance.get_daily_activity.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["activity", "today", "--dataframe"])
        assert result.exit_code == 0

    @patch("ouracli.cli.OuraClient")
    def test_format_markdown(self, mock_client: Mock) -> None:
        """Test markdown format option."""
        mock_instance = Mock()
        mock_instance.get_daily_activity.return_value = {"data": [{"id": "1"}]}
        mock_client.return_value = mock_instance

        result = runner.invoke(app, ["activity", "today", "--markdown"])
        assert result.exit_code == 0
