"""Extended tests for formatters module."""

import json

from ouracli.formatters import (
    create_ascii_bar_chart,
    create_chartjs_config,
    create_mermaid_bar_chart,
    format_html,
    format_json,
    format_markdown,
    format_output,
    format_tree,
    humanize_key,
    reorganize_by_day,
    sort_dict_keys,
)


class TestHumanizeKey:
    """Tests for humanize_key function."""

    def test_simple_key(self) -> None:
        """Test simple key humanization."""
        assert humanize_key("user_name") == "User Name"

    def test_abbreviation_rem(self) -> None:
        """Test REM abbreviation."""
        assert humanize_key("rem_sleep") == "REM Sleep"

    def test_abbreviation_spo2(self) -> None:
        """Test SPO2 abbreviation."""
        assert humanize_key("average_spo2") == "Average SPO2"

    def test_abbreviation_hrv(self) -> None:
        """Test HRV abbreviation."""
        assert humanize_key("hrv_score") == "HRV Score"

    def test_abbreviation_met(self) -> None:
        """Test MET abbreviation."""
        assert humanize_key("met_value") == "MET Value"

    def test_multiple_words(self) -> None:
        """Test multiple word key."""
        assert humanize_key("total_calories_burned") == "Total Calories Burned"

    def test_no_underscores(self) -> None:
        """Test key without underscores."""
        assert humanize_key("activity") == "Activity"


class TestSortDictKeys:
    """Tests for sort_dict_keys function."""

    def test_priority_fields_first(self) -> None:
        """Test that priority fields come first."""
        data = {"score": 100, "name": "Test", "day": "2025-01-01"}
        result = sort_dict_keys(data)
        assert result[0] == "day"
        assert result[1] == "score"
        assert result[2] == "name"

    def test_alphabetical_sorting(self) -> None:
        """Test alphabetical sorting of non-priority fields."""
        data = {"zebra": 1, "apple": 2, "banana": 3}
        result = sort_dict_keys(data)
        assert result == ["apple", "banana", "zebra"]

    def test_met_at_end(self) -> None:
        """Test that met field appears at the end."""
        data = {"day": "2025-01-01", "score": 100, "met": {}, "name": "Test"}
        result = sort_dict_keys(data)
        assert result[-1] == "met"
        assert result[0] == "day"


class TestCreateAsciiBarChart:
    """Tests for create_ascii_bar_chart function."""

    def test_empty_items(self) -> None:
        """Test with empty items list."""
        result = create_ascii_bar_chart([])
        assert result == "No MET data"

    def test_chart_dimensions(self) -> None:
        """Test chart has correct dimensions."""
        items = [1.5] * 1440  # Full day of data
        result = create_ascii_bar_chart(items)
        lines = result.split("\n")
        # Should have 10 rows + baseline + hour labels = 12 lines
        assert len(lines) == 12

    def test_hour_labels(self) -> None:
        """Test hour labels are present."""
        items = [1.5] * 1440
        result = create_ascii_bar_chart(items)
        assert " 0  1  2  3" in result
        assert "23 " in result

    def test_max_value_displayed(self) -> None:
        """Test max value is displayed in Y-axis labels."""
        items = [2.5] * 1440
        result = create_ascii_bar_chart(items)
        # The max value should appear as a Y-axis label (rounded)
        # Looking for "2" or "3" as Y-axis label since it's rounded to .0f
        lines = result.split("\n")
        # First line should have the max value as Y-axis label
        assert lines[0].strip().startswith(("2", "3"))


class TestCreateMermaidBarChart:
    """Tests for create_mermaid_bar_chart function."""

    def test_mermaid_format(self) -> None:
        """Test Mermaid chart format."""
        items = [1.5] * 1440
        result = create_mermaid_bar_chart(items)
        assert "```mermaid" in result
        assert "xychart-beta" in result
        assert "24-Hour MET Activity" in result

    def test_hourly_aggregation(self) -> None:
        """Test hourly data aggregation."""
        items = [1.0] * 60 + [2.0] * 60 + [3.0] * (1440 - 120)
        result = create_mermaid_bar_chart(items)
        # Should have 24 hour labels
        assert '"00"' in result
        assert '"23"' in result

    def test_dark_theme(self) -> None:
        """Test dark theme is applied."""
        items = [1.5] * 1440
        result = create_mermaid_bar_chart(items)
        assert "'theme':'dark'" in result


class TestCreateChartjsConfig:
    """Tests for create_chartjs_config function."""

    def test_chartjs_format(self) -> None:
        """Test Chart.js configuration format."""
        items = [1.5] * 1440
        result = create_chartjs_config(items, "chart1")
        assert "new Chart" in result
        assert "chart1" in result
        assert "type: 'bar'" in result

    def test_hourly_data(self) -> None:
        """Test 5-minute resolution data points."""
        items = [1.5] * 1440
        result = create_chartjs_config(items, "test")
        # Should have 288 data points (5-minute buckets: 24 hours * 12)
        # Data is now numeric (not string), so check for the numeric value
        assert result.count("1.5") == 288

    def test_custom_chart_id(self) -> None:
        """Test custom chart ID."""
        items = [1.5] * 1440
        result = create_chartjs_config(items, "custom_id_123")
        assert "custom_id_123" in result


class TestFormatTreeExtended:
    """Extended tests for format_tree function."""

    def test_met_field_excluded_items(self) -> None:
        """Test MET field shows chart not raw items."""
        data = {"day": "2025-01-01", "met": {"interval": 60.0, "items": [1.5] * 1440}}
        result = format_tree(data)
        assert "MET" in result
        assert "Interval" in result
        assert "Activity Chart:" in result
        # Should not show raw items list
        assert "[1.5, 1.5, 1.5" not in result

    def test_excluded_fields(self) -> None:
        """Test excluded fields are not shown."""
        data = {"id": "123", "timestamp": "2025-01-01", "name": "Test"}
        result = format_tree(data)
        assert "id" not in result.lower()
        assert "timestamp" not in result.lower()
        assert "Name" in result

    def test_class_5_min_excluded(self) -> None:
        """Test class_5_min field is excluded."""
        data = {"day": "2025-01-01", "class_5_min": "data", "score": 100}
        result = format_tree(data)
        assert "class" not in result.lower()
        assert "Score" in result

    def test_empty_lists_skipped(self) -> None:
        """Test empty lists are skipped."""
        data = {"name": "Test", "items": []}
        result = format_tree(data)
        assert "items" not in result.lower()

    def test_contributors_formatting(self) -> None:
        """Test contributors dict formatting."""
        data = {"contributors": {"meet_daily_targets": 100, "stay_active": 80}}
        result = format_tree(data)
        assert "Contributors" in result
        assert "Meet Daily Targets" in result
        assert "Stay Active" in result

    def test_dot_leader_alignment(self) -> None:
        """Test dot leaders align values."""
        data = {"short": 1, "very_long_field_name": 2}
        result = format_tree(data)
        lines = result.split("\n")
        # Both lines should have dots before values
        assert "..." in lines[0]
        assert "..." in lines[1]


class TestFormatJsonExtended:
    """Extended tests for format_json function."""

    def test_met_items_single_line(self) -> None:
        """Test MET items array is on single line."""
        data = {"met": {"interval": 60.0, "items": [1.0, 1.1, 1.2, 1.3, 1.4]}}
        result = format_json(data)
        # Items should be on one line
        assert '"items": [1.0, 1.1, 1.2, 1.3, 1.4]' in result
        # Should have newlines for outer structure
        assert "\n" in result

    def test_nested_structure_preserved(self) -> None:
        """Test nested structure is preserved."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 100}, {"day": "2025-01-02", "score": 90}]
        }
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_met_with_long_array(self) -> None:
        """Test MET with full day of data."""
        data = {"met": {"interval": 60.0, "items": [1.5] * 1440}}
        result = format_json(data)
        # Should parse as valid JSON
        parsed = json.loads(result)
        assert len(parsed["met"]["items"]) == 1440
        # Items should be on one line (no newlines within items array)
        items_line = [line for line in result.split("\n") if '"items":' in line][0]
        assert items_line.count("[") == 1
        assert items_line.count("]") == 1


class TestFormatMarkdownExtended:
    """Extended tests for format_markdown function."""

    def test_heading_hierarchy(self) -> None:
        """Test proper heading hierarchy."""
        data = {"activity": [{"day": "2025-01-01", "score": 100}]}
        result = format_markdown(data)
        assert "# Activity" in result
        assert "## 2025-01-01" in result

    def test_table_format(self) -> None:
        """Test tables are used for key-value pairs."""
        data = {"activity": [{"day": "2025-01-01", "score": 100, "steps": 5000}]}
        result = format_markdown(data)
        assert "| Field | Value |" in result
        assert "|-------|-------|" in result
        assert "| Score | 100 |" in result

    def test_mermaid_chart_included(self) -> None:
        """Test Mermaid chart is included for MET data."""
        data = {
            "activity": [{"day": "2025-01-01", "met": {"interval": 60.0, "items": [1.5] * 1440}}]
        }
        result = format_markdown(data)
        assert "```mermaid" in result
        assert "xychart-beta" in result

    def test_contributors_as_table(self) -> None:
        """Test contributors dict becomes table."""
        data = {
            "activity": [
                {
                    "day": "2025-01-01",
                    "contributors": {"meet_daily_targets": 100, "stay_active": 80},
                }
            ]
        }
        result = format_markdown(data)
        assert "### Contributors" in result
        assert "| Meet Daily Targets | 100 |" in result


class TestFormatHtmlExtended:
    """Extended tests for format_html function."""

    def test_html_structure(self) -> None:
        """Test HTML document structure."""
        data = {"activity": [{"day": "2025-01-01", "score": 100}]}
        result = format_html(data)
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "<head>" in result
        assert "<body>" in result

    def test_chartjs_included(self) -> None:
        """Test Chart.js library is included."""
        data = {"activity": [{"day": "2025-01-01"}]}
        result = format_html(data)
        assert "chart.js" in result
        assert "<script" in result

    def test_chartjs_for_met_data(self) -> None:
        """Test Chart.js chart is created for MET data."""
        data = {
            "activity": [{"day": "2025-01-01", "met": {"interval": 60.0, "items": [1.5] * 1440}}]
        }
        result = format_html(data)
        assert "new Chart" in result
        assert "canvas" in result

    def test_css_styling(self) -> None:
        """Test CSS styling is included."""
        data = {"activity": [{"day": "2025-01-01"}]}
        result = format_html(data)
        assert "<style>" in result
        assert "table" in result
        assert "font-family" in result

    def test_tables_for_data(self) -> None:
        """Test HTML tables are used for data."""
        data = {"activity": [{"day": "2025-01-01", "score": 100}]}
        result = format_html(data)
        assert "<table>" in result
        assert "<tr>" in result
        assert "<td>" in result


class TestReorganizeByDay:
    """Tests for reorganize_by_day function."""

    def test_basic_reorganization(self) -> None:
        """Test basic data reorganization."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 100}, {"day": "2025-01-02", "score": 90}],
            "sleep": [{"day": "2025-01-01", "score": 80}, {"day": "2025-01-02", "score": 85}],
        }
        result = reorganize_by_day(data)
        assert "2025-01-01" in result
        assert "2025-01-02" in result
        assert result["2025-01-01"]["activity"]["score"] == 100
        assert result["2025-01-01"]["sleep"]["score"] == 80

    def test_chronological_sorting(self) -> None:
        """Test days are sorted chronologically."""
        data = {
            "activity": [
                {"day": "2025-01-03", "score": 100},
                {"day": "2025-01-01", "score": 90},
                {"day": "2025-01-02", "score": 95},
            ]
        }
        result = reorganize_by_day(data)
        days = list(result.keys())
        assert days == ["2025-01-01", "2025-01-02", "2025-01-03"]

    def test_missing_data_handling(self) -> None:
        """Test handling of missing data for some days."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 100}, {"day": "2025-01-02", "score": 90}],
            "sleep": [
                {"day": "2025-01-01", "score": 80}
                # No sleep data for 2025-01-02
            ],
        }
        result = reorganize_by_day(data)
        assert "activity" in result["2025-01-01"]
        assert "sleep" in result["2025-01-01"]
        assert "activity" in result["2025-01-02"]
        assert "sleep" not in result["2025-01-02"]


class TestFormatOutputExtended:
    """Extended tests for format_output function."""

    def test_html_format(self) -> None:
        """Test HTML format output."""
        data = {"activity": [{"day": "2025-01-01", "score": 100}]}
        result = format_output(data, "html")
        assert "<!DOCTYPE html>" in result

    def test_by_day_flag(self) -> None:
        """Test by_day flag reorganizes data."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 100}],
            "sleep": [{"day": "2025-01-01", "score": 80}],
        }
        result = format_output(data, "tree", by_day=True)
        # Should show day first, then methods
        assert "2025-01-01" in result
        assert "Activity" in result

    def test_by_day_false(self) -> None:
        """Test by_day=False keeps original structure."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 100}],
            "sleep": [{"day": "2025-01-01", "score": 80}],
        }
        result = format_output(data, "tree", by_day=False)
        # Should show methods as top-level
        lines = result.split("\n")
        # First non-empty line should be a method name
        first_line = [line for line in lines if line.strip()][0]
        assert "Activity" in first_line or "Sleep" in first_line


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_activity_data_tree(self) -> None:
        """Test full activity data formatting in tree."""
        data = {
            "day": "2025-01-01",
            "score": 85,
            "steps": 10000,
            "contributors": {"meet_daily_targets": 100, "stay_active": 90},
            "met": {"interval": 60.0, "items": [1.5] * 1440},
        }
        result = format_tree(data)
        assert "Day" in result
        assert "Score" in result
        assert "Contributors" in result
        assert "MET" in result
        assert "Activity Chart:" in result

    def test_full_activity_data_json(self) -> None:
        """Test full activity data formatting in JSON."""
        data = {"day": "2025-01-01", "met": {"interval": 60.0, "items": [1.5] * 1440}}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed["day"] == "2025-01-01"
        assert len(parsed["met"]["items"]) == 1440

    def test_full_activity_data_markdown(self) -> None:
        """Test full activity data formatting in markdown."""
        data = {
            "activity": [
                {"day": "2025-01-01", "score": 85, "met": {"interval": 60.0, "items": [1.5] * 1440}}
            ]
        }
        result = format_markdown(data)
        assert "# Activity" in result
        assert "## 2025-01-01" in result
        assert "### MET" in result
        assert "```mermaid" in result

    def test_multiple_days_by_day(self) -> None:
        """Test multiple days with by_day organization."""
        data = {
            "activity": [{"day": "2025-01-01", "score": 85}, {"day": "2025-01-02", "score": 90}],
            "sleep": [{"day": "2025-01-01", "score": 75}, {"day": "2025-01-02", "score": 80}],
        }
        result = format_output(data, "tree", by_day=True)
        # Should show days as top level
        assert "2025-01-01" in result
        assert "2025-01-02" in result
