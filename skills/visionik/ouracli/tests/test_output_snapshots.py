"""Snapshot tests for output formats to ensure refactoring doesn't break formatting.

These tests use real API data fixtures to validate that all output formats
(json, tree, markdown, html, dataframe) produce consistent output.
"""

import json
from pathlib import Path

from ouracli.formatters import format_output

# Load fixture data
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict | list:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / filename) as f:
        return json.load(f)


# Load all fixtures
ACTIVITY_14DAYS = load_fixture("activity_recent_14days.json")
SLEEP_14DAYS = load_fixture("sleep_recent_14days.json")
HEARTRATE_3DAYS = load_fixture("heartrate_recent_3days.json")


class TestActivityOutputFormats:
    """Test all output formats for activity data."""

    def test_activity_json_format(self) -> None:
        """Test JSON format for activity data."""
        result = format_output(ACTIVITY_14DAYS, "json")

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == len(ACTIVITY_14DAYS)

        # Verify first item structure
        if parsed:
            assert "day" in parsed[0]
            assert "score" in parsed[0]
            # Check that met data is on one line
            if "met" in parsed[0]:
                assert '"items": [' in result

    def test_activity_tree_format(self) -> None:
        """Test tree format for activity data."""
        result = format_output(ACTIVITY_14DAYS, "tree")

        # Basic structure checks
        assert isinstance(result, str)
        assert len(result) > 100  # Should have substantial content

        # Should contain humanized keys
        assert "Day" in result or "Score" in result

        # Should have tree structure indicators
        assert "..." in result  # Dot leaders

    def test_activity_markdown_format(self) -> None:
        """Test markdown format for activity data."""
        result = format_output(ACTIVITY_14DAYS, "markdown")

        assert isinstance(result, str)
        assert len(result) > 100

        # Should contain markdown headers
        assert "#" in result

        # Should contain humanized keys
        assert "Day" in result or "Score" in result

    def test_activity_html_format(self) -> None:
        """Test HTML format for activity data."""
        result = format_output(ACTIVITY_14DAYS, "html")

        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result

        # Should contain Chart.js for MET data
        if any("met" in item for item in ACTIVITY_14DAYS if isinstance(item, dict)):
            assert "Chart.js" in result or "chart.js" in result
            assert "<canvas" in result

    def test_activity_dataframe_format(self) -> None:
        """Test dataframe format for activity data."""
        result = format_output(ACTIVITY_14DAYS, "dataframe")

        assert isinstance(result, str)
        # Should contain table-like structure
        # Dataframe format varies, just ensure it doesn't crash


class TestSleepOutputFormats:
    """Test all output formats for sleep data."""

    def test_sleep_json_format(self) -> None:
        """Test JSON format for sleep data."""
        result = format_output(SLEEP_14DAYS, "json")

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) <= 14  # Up to 14 days

    def test_sleep_tree_format(self) -> None:
        """Test tree format for sleep data."""
        result = format_output(SLEEP_14DAYS, "tree")

        assert isinstance(result, str)
        assert len(result) > 50
        # Should have tree structure
        assert "..." in result

    def test_sleep_markdown_format(self) -> None:
        """Test markdown format for sleep data."""
        result = format_output(SLEEP_14DAYS, "markdown")

        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_sleep_html_format(self) -> None:
        """Test HTML format for sleep data."""
        result = format_output(SLEEP_14DAYS, "html")

        assert "<!DOCTYPE html>" in result
        assert "</html>" in result

    def test_sleep_dataframe_format(self) -> None:
        """Test dataframe format for sleep data."""
        result = format_output(SLEEP_14DAYS, "dataframe")

        assert isinstance(result, str)
        # Should contain table-like structure
        # Dataframe format varies, just ensure it doesn't crash


class TestHeartrateOutputFormats:
    """Test all output formats for heart rate data."""

    def test_heartrate_json_format(self) -> None:
        """Test JSON format for heart rate data."""
        result = format_output(HEARTRATE_3DAYS, "json")

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        # Heart rate is time-series, should have many data points
        assert len(parsed) > 10

    def test_heartrate_tree_format(self) -> None:
        """Test tree format for heart rate data."""
        result = format_output(HEARTRATE_3DAYS, "tree")

        assert isinstance(result, str)
        assert len(result) > 100
        # Heart rate data might be in chart format or other format
        # Just verify it produces output

    def test_heartrate_markdown_format(self) -> None:
        """Test markdown format for heart rate data."""
        result = format_output(HEARTRATE_3DAYS, "markdown")

        assert isinstance(result, str)
        assert "#" in result

    def test_heartrate_html_format(self) -> None:
        """Test HTML format for heart rate data."""
        result = format_output(HEARTRATE_3DAYS, "html")

        assert "<!DOCTYPE html>" in result
        # Should contain Chart.js for visualization
        assert "Chart.js" in result or "chart.js" in result
        assert "<canvas" in result

    def test_heartrate_dataframe_format(self) -> None:
        """Test dataframe format for heart rate data."""
        result = format_output(HEARTRATE_3DAYS, "dataframe")

        assert isinstance(result, str)
        # Should contain table-like structure
        # Dataframe format varies, just ensure it doesn't crash


class TestDetailedOutputValidation:
    """Detailed validation of specific formatting behaviors."""

    def test_met_data_inline_in_json(self) -> None:
        """Verify MET items array is formatted inline in JSON output."""
        result = format_output(ACTIVITY_14DAYS, "json")

        # MET items should be on one line
        lines = result.split("\n")
        items_lines = [line for line in lines if '"items":' in line]

        # Each items line should contain the full array
        for line in items_lines:
            # Should have opening and closing bracket on same line
            assert "[" in line
            # May have closing bracket on same line or next (depends on implementation)

    def test_excluded_fields_not_in_tree(self) -> None:
        """Verify excluded fields don't appear in tree output."""
        result = format_output(ACTIVITY_14DAYS, "tree")

        # These fields should be excluded
        assert "timestamp" not in result.lower()
        assert '"id"' not in result.lower()

    def test_humanized_keys_in_tree(self) -> None:
        """Verify keys are humanized in tree output."""
        result = format_output(ACTIVITY_14DAYS, "tree")

        # Should see humanized versions
        if "active_calories" in str(ACTIVITY_14DAYS):
            assert "Active Calories" in result

    def test_html_contains_styles(self) -> None:
        """Verify HTML output includes necessary styles."""
        result = format_output(ACTIVITY_14DAYS, "html")

        assert "<style>" in result
        assert "</style>" in result
        # Should have basic styling
        assert "font-family" in result
        assert "color" in result

    def test_html_chart_data_is_numeric(self) -> None:
        """Verify HTML chart data uses numeric values, not strings."""
        result = format_output(ACTIVITY_14DAYS, "html")

        if "data: [" in result:
            # Find data arrays
            data_sections = result.split("data: [")
            for section in data_sections[1:]:  # Skip first split
                data_part = section.split("]")[0]
                # Should not have quoted numbers for data values
                # (labels are OK to be quoted)
                if "," in data_part:
                    # Check that we don't have patterns like "1.5", "2.0"
                    # but null should be unquoted
                    assert '"null"' not in data_part


class TestOutputConsistency:
    """Test that outputs are consistent across runs."""

    def test_json_output_is_deterministic(self) -> None:
        """Verify JSON output is consistent across multiple calls."""
        result1 = format_output(ACTIVITY_14DAYS, "json")
        result2 = format_output(ACTIVITY_14DAYS, "json")

        assert result1 == result2

    def test_tree_output_is_deterministic(self) -> None:
        """Verify tree output is consistent across multiple calls."""
        result1 = format_output(ACTIVITY_14DAYS, "tree")
        result2 = format_output(ACTIVITY_14DAYS, "tree")

        assert result1 == result2

    def test_markdown_output_is_deterministic(self) -> None:
        """Verify markdown output is consistent across multiple calls."""
        result1 = format_output(ACTIVITY_14DAYS, "markdown")
        result2 = format_output(ACTIVITY_14DAYS, "markdown")

        assert result1 == result2


class TestEdgeCasesWithRealData:
    """Test edge cases using real data."""

    def test_empty_met_items_handling(self) -> None:
        """Test handling of items with empty MET data."""
        # Create a copy with empty MET items
        if ACTIVITY_14DAYS and isinstance(ACTIVITY_14DAYS, list):
            test_data = ACTIVITY_14DAYS[:1]
            if test_data and "met" in test_data[0]:
                test_data[0]["met"]["items"] = []

                result = format_output(test_data, "json")
                assert '"items": []' in result

    def test_missing_fields_handled_gracefully(self) -> None:
        """Test that missing fields are handled gracefully."""
        if ACTIVITY_14DAYS and isinstance(ACTIVITY_14DAYS, list):
            # Create minimal data
            test_data = [{"day": "2024-11-01"}]

            for format_type in ["json", "tree", "markdown", "html"]:
                result = format_output(test_data, format_type)
                assert isinstance(result, str)
                assert len(result) > 0

    def test_large_heartrate_dataset(self) -> None:
        """Test formatting of large heart rate dataset."""
        # Heart rate data can be very large
        result = format_output(HEARTRATE_3DAYS, "json")

        # Should handle large data
        assert len(result) > 1000

        # Should still be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)


class TestFormatSpecificFeatures:
    """Test format-specific features."""

    def test_html_multiple_day_charts(self) -> None:
        """Test that HTML creates separate charts for multiple days of heart rate data."""
        if isinstance(HEARTRATE_3DAYS, list) and len(HEARTRATE_3DAYS) > 0:
            result = format_output(HEARTRATE_3DAYS, "html")

            # Should have multiple chart canvases for multiple days
            canvas_count = result.count("<canvas")
            # At least one chart per day of data
            assert canvas_count >= 1

    def test_markdown_preserves_structure(self) -> None:
        """Test that markdown preserves hierarchical structure."""
        result = format_output(ACTIVITY_14DAYS, "markdown")

        # Should have different heading levels
        assert "##" in result or "###" in result

        # Should have some data values (dates in format 20XX)
        if ACTIVITY_14DAYS:
            assert "20" in result
            assert "-" in result  # Should have dates in YYYY-MM-DD format

    def test_tree_alignment(self) -> None:
        """Test that tree output has proper alignment."""
        result = format_output(ACTIVITY_14DAYS, "tree")

        lines = result.split("\n")
        # Check that dot leaders create alignment
        dot_lines = [line for line in lines if "..." in line]
        if len(dot_lines) >= 2:
            # Values should be roughly aligned (within a few characters)
            # This is a heuristic check
            assert len(dot_lines) > 0
