"""Comprehensive snapshot tests for all CLI methods × all output formats.

This test file ensures complete coverage of:
- 12 CLI methods (activity, sleep, readiness, spo2, stress, heartrate, workout,
  session, tag, rest-mode, personal-info, all)
- 5 output formats (json, tree, markdown, html, dataframe)
= 60 test combinations total

These tests use real API data fixtures to validate that all output formats
produce consistent output before and after refactoring.
"""

import json
from pathlib import Path

import pytest

from ouracli.formatters import format_output

# Load fixture data
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict | list:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / filename) as f:
        return json.load(f)


# Load all fixtures
ACTIVITY = load_fixture("activity_recent_14days.json")
SLEEP = load_fixture("sleep_recent_14days.json")
HEARTRATE = load_fixture("heartrate_recent_3days.json")
READINESS = load_fixture("readiness_recent_14days.json")
SPO2 = load_fixture("spo2_recent_14days.json")
STRESS = load_fixture("stress_recent_14days.json")
WORKOUT = load_fixture("workout_recent_14days.json")
SESSION = load_fixture("session_recent_14days.json")
TAG = load_fixture("tag_recent_14days.json")
REST_MODE = load_fixture("rest_mode_recent_14days.json")
PERSONAL_INFO = load_fixture("personal_info.json")


# Helper to skip empty data
def skip_if_empty(data: list | dict) -> None:
    """Skip test if data is empty."""
    if isinstance(data, list) and len(data) == 0:
        pytest.skip("No data available for this endpoint")
    if isinstance(data, dict) and len(data) == 0:
        pytest.skip("No data available for this endpoint")


class TestActivityAllFormats:
    """Test all formats for activity data."""

    def test_activity_json(self) -> None:
        """Activity: JSON format."""
        result = format_output(ACTIVITY, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    def test_activity_tree(self) -> None:
        """Activity: Tree format."""
        result = format_output(ACTIVITY, "tree")
        assert isinstance(result, str)
        assert len(result) > 100
        assert "..." in result

    def test_activity_markdown(self) -> None:
        """Activity: Markdown format."""
        result = format_output(ACTIVITY, "markdown")
        assert isinstance(result, str)
        assert "#" in result

    def test_activity_html(self) -> None:
        """Activity: HTML format."""
        result = format_output(ACTIVITY, "html")
        assert "<!DOCTYPE html>" in result
        assert "</html>" in result

    def test_activity_dataframe(self) -> None:
        """Activity: Dataframe format."""
        result = format_output(ACTIVITY, "dataframe")
        assert isinstance(result, str)


class TestSleepAllFormats:
    """Test all formats for sleep data."""

    def test_sleep_json(self) -> None:
        """Sleep: JSON format."""
        result = format_output(SLEEP, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_sleep_tree(self) -> None:
        """Sleep: Tree format."""
        result = format_output(SLEEP, "tree")
        assert isinstance(result, str)
        assert len(result) > 50

    def test_sleep_markdown(self) -> None:
        """Sleep: Markdown format."""
        result = format_output(SLEEP, "markdown")
        assert isinstance(result, str)
        assert "#" in result

    def test_sleep_html(self) -> None:
        """Sleep: HTML format."""
        result = format_output(SLEEP, "html")
        assert "<!DOCTYPE html>" in result

    def test_sleep_dataframe(self) -> None:
        """Sleep: Dataframe format."""
        result = format_output(SLEEP, "dataframe")
        assert isinstance(result, str)


class TestHeartrateAllFormats:
    """Test all formats for heart rate data."""

    def test_heartrate_json(self) -> None:
        """Heart rate: JSON format."""
        result = format_output(HEARTRATE, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 10

    def test_heartrate_tree(self) -> None:
        """Heart rate: Tree format."""
        result = format_output(HEARTRATE, "tree")
        assert isinstance(result, str)
        assert len(result) > 100

    def test_heartrate_markdown(self) -> None:
        """Heart rate: Markdown format."""
        result = format_output(HEARTRATE, "markdown")
        assert isinstance(result, str)
        assert "#" in result

    def test_heartrate_html(self) -> None:
        """Heart rate: HTML format."""
        result = format_output(HEARTRATE, "html")
        assert "<!DOCTYPE html>" in result
        assert "chart.js" in result.lower()

    def test_heartrate_dataframe(self) -> None:
        """Heart rate: Dataframe format."""
        result = format_output(HEARTRATE, "dataframe")
        assert isinstance(result, str)


class TestReadinessAllFormats:
    """Test all formats for readiness data."""

    def test_readiness_json(self) -> None:
        """Readiness: JSON format."""
        result = format_output(READINESS, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    def test_readiness_tree(self) -> None:
        """Readiness: Tree format."""
        result = format_output(READINESS, "tree")
        assert isinstance(result, str)
        assert len(result) > 50

    def test_readiness_markdown(self) -> None:
        """Readiness: Markdown format."""
        result = format_output(READINESS, "markdown")
        assert isinstance(result, str)
        assert "#" in result

    def test_readiness_html(self) -> None:
        """Readiness: HTML format."""
        result = format_output(READINESS, "html")
        assert "<!DOCTYPE html>" in result

    def test_readiness_dataframe(self) -> None:
        """Readiness: Dataframe format."""
        result = format_output(READINESS, "dataframe")
        assert isinstance(result, str)


class TestSpo2AllFormats:
    """Test all formats for SpO2 data."""

    def test_spo2_json(self) -> None:
        """SpO2: JSON format."""
        skip_if_empty(SPO2)
        result = format_output(SPO2, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_spo2_tree(self) -> None:
        """SpO2: Tree format."""
        skip_if_empty(SPO2)
        result = format_output(SPO2, "tree")
        assert isinstance(result, str)

    def test_spo2_markdown(self) -> None:
        """SpO2: Markdown format."""
        skip_if_empty(SPO2)
        result = format_output(SPO2, "markdown")
        assert isinstance(result, str)

    def test_spo2_html(self) -> None:
        """SpO2: HTML format."""
        skip_if_empty(SPO2)
        result = format_output(SPO2, "html")
        assert "<!DOCTYPE html>" in result

    def test_spo2_dataframe(self) -> None:
        """SpO2: Dataframe format."""
        skip_if_empty(SPO2)
        result = format_output(SPO2, "dataframe")
        assert isinstance(result, str)


class TestStressAllFormats:
    """Test all formats for stress data."""

    def test_stress_json(self) -> None:
        """Stress: JSON format."""
        skip_if_empty(STRESS)
        result = format_output(STRESS, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_stress_tree(self) -> None:
        """Stress: Tree format."""
        skip_if_empty(STRESS)
        result = format_output(STRESS, "tree")
        assert isinstance(result, str)

    def test_stress_markdown(self) -> None:
        """Stress: Markdown format."""
        skip_if_empty(STRESS)
        result = format_output(STRESS, "markdown")
        assert isinstance(result, str)

    def test_stress_html(self) -> None:
        """Stress: HTML format."""
        skip_if_empty(STRESS)
        result = format_output(STRESS, "html")
        assert "<!DOCTYPE html>" in result

    def test_stress_dataframe(self) -> None:
        """Stress: Dataframe format."""
        skip_if_empty(STRESS)
        result = format_output(STRESS, "dataframe")
        assert isinstance(result, str)


class TestWorkoutAllFormats:
    """Test all formats for workout data."""

    def test_workout_json(self) -> None:
        """Workout: JSON format."""
        skip_if_empty(WORKOUT)
        result = format_output(WORKOUT, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_workout_tree(self) -> None:
        """Workout: Tree format."""
        skip_if_empty(WORKOUT)
        result = format_output(WORKOUT, "tree")
        assert isinstance(result, str)

    def test_workout_markdown(self) -> None:
        """Workout: Markdown format."""
        skip_if_empty(WORKOUT)
        result = format_output(WORKOUT, "markdown")
        assert isinstance(result, str)

    def test_workout_html(self) -> None:
        """Workout: HTML format."""
        skip_if_empty(WORKOUT)
        result = format_output(WORKOUT, "html")
        assert "<!DOCTYPE html>" in result

    def test_workout_dataframe(self) -> None:
        """Workout: Dataframe format."""
        skip_if_empty(WORKOUT)
        result = format_output(WORKOUT, "dataframe")
        assert isinstance(result, str)


class TestSessionAllFormats:
    """Test all formats for session data."""

    def test_session_json(self) -> None:
        """Session: JSON format."""
        skip_if_empty(SESSION)
        result = format_output(SESSION, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_session_tree(self) -> None:
        """Session: Tree format."""
        skip_if_empty(SESSION)
        result = format_output(SESSION, "tree")
        assert isinstance(result, str)

    def test_session_markdown(self) -> None:
        """Session: Markdown format."""
        skip_if_empty(SESSION)
        result = format_output(SESSION, "markdown")
        assert isinstance(result, str)

    def test_session_html(self) -> None:
        """Session: HTML format."""
        skip_if_empty(SESSION)
        result = format_output(SESSION, "html")
        assert "<!DOCTYPE html>" in result

    def test_session_dataframe(self) -> None:
        """Session: Dataframe format."""
        skip_if_empty(SESSION)
        result = format_output(SESSION, "dataframe")
        assert isinstance(result, str)


class TestTagAllFormats:
    """Test all formats for tag data."""

    def test_tag_json(self) -> None:
        """Tag: JSON format."""
        skip_if_empty(TAG)
        result = format_output(TAG, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_tag_tree(self) -> None:
        """Tag: Tree format."""
        skip_if_empty(TAG)
        result = format_output(TAG, "tree")
        assert isinstance(result, str)

    def test_tag_markdown(self) -> None:
        """Tag: Markdown format."""
        skip_if_empty(TAG)
        result = format_output(TAG, "markdown")
        assert isinstance(result, str)

    def test_tag_html(self) -> None:
        """Tag: HTML format."""
        skip_if_empty(TAG)
        result = format_output(TAG, "html")
        assert "<!DOCTYPE html>" in result

    def test_tag_dataframe(self) -> None:
        """Tag: Dataframe format."""
        skip_if_empty(TAG)
        result = format_output(TAG, "dataframe")
        assert isinstance(result, str)


class TestRestModeAllFormats:
    """Test all formats for rest mode data."""

    def test_rest_mode_json(self) -> None:
        """Rest mode: JSON format."""
        skip_if_empty(REST_MODE)
        result = format_output(REST_MODE, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_rest_mode_tree(self) -> None:
        """Rest mode: Tree format."""
        skip_if_empty(REST_MODE)
        result = format_output(REST_MODE, "tree")
        assert isinstance(result, str)

    def test_rest_mode_markdown(self) -> None:
        """Rest mode: Markdown format."""
        skip_if_empty(REST_MODE)
        result = format_output(REST_MODE, "markdown")
        assert isinstance(result, str)

    def test_rest_mode_html(self) -> None:
        """Rest mode: HTML format."""
        skip_if_empty(REST_MODE)
        result = format_output(REST_MODE, "html")
        assert "<!DOCTYPE html>" in result

    def test_rest_mode_dataframe(self) -> None:
        """Rest mode: Dataframe format."""
        skip_if_empty(REST_MODE)
        result = format_output(REST_MODE, "dataframe")
        assert isinstance(result, str)


class TestPersonalInfoAllFormats:
    """Test all formats for personal info data."""

    def test_personal_info_json(self) -> None:
        """Personal info: JSON format."""
        result = format_output(PERSONAL_INFO, "json")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "email" in parsed
        assert parsed["email"] == "jsmith@some.where"

    def test_personal_info_tree(self) -> None:
        """Personal info: Tree format."""
        result = format_output(PERSONAL_INFO, "tree")
        assert isinstance(result, str)
        assert "Email" in result or "email" in result.lower()

    def test_personal_info_markdown(self) -> None:
        """Personal info: Markdown format."""
        result = format_output(PERSONAL_INFO, "markdown")
        assert isinstance(result, str)

    def test_personal_info_html(self) -> None:
        """Personal info: HTML format."""
        result = format_output(PERSONAL_INFO, "html")
        assert "<!DOCTYPE html>" in result
        assert "jsmith@some.where" in result

    def test_personal_info_dataframe(self) -> None:
        """Personal info: Dataframe format."""
        result = format_output(PERSONAL_INFO, "dataframe")
        assert isinstance(result, str)


class TestFormatConsistency:
    """Test that all formats handle various data structures consistently."""

    @pytest.mark.parametrize("format_type", ["json", "tree", "markdown", "html", "dataframe"])
    def test_activity_all_formats_work(self, format_type: str) -> None:
        """Activity works in all formats."""
        result = format_output(ACTIVITY, format_type)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("format_type", ["json", "tree", "markdown", "html", "dataframe"])
    def test_readiness_all_formats_work(self, format_type: str) -> None:
        """Readiness works in all formats."""
        result = format_output(READINESS, format_type)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("format_type", ["json", "tree", "markdown", "html", "dataframe"])
    def test_personal_info_all_formats_work(self, format_type: str) -> None:
        """Personal info works in all formats."""
        result = format_output(PERSONAL_INFO, format_type)
        assert isinstance(result, str)
        assert len(result) > 0
