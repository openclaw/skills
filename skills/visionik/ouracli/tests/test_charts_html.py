"""Tests for charts_html module."""

from ouracli.charts_html import create_chartjs_config, create_chartjs_heartrate_config


class TestCreateChartjsHeartrateConfig:
    """Tests for create_chartjs_heartrate_config function."""

    def test_empty_data(self) -> None:
        """Test with empty heart rate data."""
        result = create_chartjs_heartrate_config([], "chart1")
        assert result == ""

    def test_no_valid_bpm_values(self) -> None:
        """Test with data that has no valid BPM values."""
        data = [
            {"timestamp": "2025-01-01T00:00:00Z", "bpm": None},
            {"timestamp": "2025-01-01T00:05:00Z", "bpm": None},
        ]
        result = create_chartjs_heartrate_config(data, "chart1")
        assert result == ""

    def test_chart_id_in_output(self) -> None:
        """Test that chart ID appears in the output."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "test_chart_123")
        assert "test_chart_123" in result
        assert "getElementById('test_chart_123')" in result

    def test_basic_structure(self) -> None:
        """Test that output contains basic Chart.js structure."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        assert "new Chart" in result
        assert "type: 'bar'" in result
        assert "labels:" in result
        assert "datasets:" in result
        assert "options:" in result

    def test_288_buckets_created(self) -> None:
        """Test that 288 5-minute buckets are created."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Extract the data array from the JavaScript output
        # Should have 288 values (one per 5-minute bucket)
        assert "data: [" in result
        # Count commas in the data array (288 values = 287 commas)
        data_section = result.split("data: [")[1].split("]")[0]
        comma_count = data_section.count(",")
        assert comma_count == 287

    def test_hour_labels(self) -> None:
        """Test that hour labels are present."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Should have labels for hours 00-23
        assert '"00"' in result
        assert '"12"' in result
        assert '"23"' in result

    def test_bpm_bucketing(self) -> None:
        """Test that BPM values are properly bucketed."""
        # Create data with specific BPM values at specific times
        data = [
            {"timestamp": "2025-01-01T00:00:00Z", "bpm": 60},
            {"timestamp": "2025-01-01T00:01:00Z", "bpm": 62},
            {"timestamp": "2025-01-01T00:02:00Z", "bpm": 64},
            {"timestamp": "2025-01-01T00:03:00Z", "bpm": 66},
            {"timestamp": "2025-01-01T00:04:00Z", "bpm": 68},
            # These should average to 64
        ]
        result = create_chartjs_heartrate_config(data, "chart1")
        # The first bucket (00:00-00:05) should contain the average
        assert "data: [64" in result

    def test_null_for_missing_buckets(self) -> None:
        """Test that null is used for buckets with no data."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Should have null values for empty buckets
        assert "null" in result

    def test_y_axis_range(self) -> None:
        """Test that Y-axis range is calculated correctly."""
        data = [
            {"timestamp": "2025-01-01T00:00:00Z", "bpm": 60},
            {"timestamp": "2025-01-01T01:00:00Z", "bpm": 120},
        ]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Min should be 60 - 10 = 50
        assert "min: 50.0" in result
        # Max should be 120
        assert "max: 120.0" in result

    def test_invalid_timestamps_skipped(self) -> None:
        """Test that invalid timestamps are skipped."""
        data = [
            {"timestamp": "invalid", "bpm": 70},
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": 75},
        ]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Should still generate output with valid data
        assert result != ""
        assert "75" in result

    def test_title_present(self) -> None:
        """Test that chart title is present."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        assert "24-Hour Heart Rate (5-minute resolution)" in result

    def test_tooltip_callback_present(self) -> None:
        """Test that tooltip callback is present."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        assert "tooltip:" in result
        assert "callbacks:" in result
        assert "title: function(context)" in result

    def test_numeric_data_not_strings(self) -> None:
        """Test that data values are numeric, not strings."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_chartjs_heartrate_config(data, "chart1")
        # Extract data array
        data_section = result.split("data: [")[1].split("]")[0]
        # Should not have quoted numbers
        assert '"70"' not in data_section
        # Should have unquoted numbers or null
        assert "70" in data_section or "null" in data_section


class TestCreateChartjsConfig:
    """Tests for create_chartjs_config function (MET data)."""

    def test_empty_data(self) -> None:
        """Test with empty MET data."""
        result = create_chartjs_config([], "chart1")
        # Should still generate output with zeros
        assert "new Chart" in result

    def test_chart_id_in_output(self) -> None:
        """Test that chart ID appears in the output."""
        result = create_chartjs_config([1.5] * 1440, "met_chart_456")
        assert "met_chart_456" in result
        assert "getElementById('met_chart_456')" in result

    def test_basic_structure(self) -> None:
        """Test that output contains basic Chart.js structure."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert "new Chart" in result
        assert "type: 'bar'" in result
        assert "labels:" in result
        assert "datasets:" in result
        assert "options:" in result

    def test_288_buckets(self) -> None:
        """Test that 288 5-minute buckets are created."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        # Should have 288 data points
        data_section = result.split("data: [")[1].split("]")[0]
        comma_count = data_section.count(",")
        assert comma_count == 287

    def test_five_minute_averaging(self) -> None:
        """Test that 5-minute averaging works correctly."""
        # Create 1440 items (24 hours * 60 minutes)
        # First 5 minutes: all 2.0
        items = [2.0] * 5
        # Rest: 1.0
        items.extend([1.0] * 1435)
        result = create_chartjs_config(items, "chart1")
        # First bucket should be 2.0
        assert "data: [2.0" in result

    def test_partial_data(self) -> None:
        """Test with partial day data."""
        # Only 100 items instead of 1440
        result = create_chartjs_config([1.5] * 100, "chart1")
        # Should still create 288 buckets, filling missing with 0
        data_section = result.split("data: [")[1].split("]")[0]
        comma_count = data_section.count(",")
        assert comma_count == 287
        # Should have some zeros for missing data
        assert "0.0" in result or "0" in result

    def test_hour_labels(self) -> None:
        """Test that hour labels are present."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert '"00"' in result
        assert '"12"' in result
        assert '"23"' in result

    def test_y_axis_max_6(self) -> None:
        """Test that Y-axis max is set to 6."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert "max: 6" in result

    def test_y_axis_begins_at_zero(self) -> None:
        """Test that Y-axis begins at zero."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert "beginAtZero: true" in result

    def test_title_present(self) -> None:
        """Test that chart title is present."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert "24-Hour MET Activity (5-minute resolution)" in result

    def test_numeric_values(self) -> None:
        """Test that values are rounded to 2 decimal places."""
        result = create_chartjs_config([1.567] * 1440, "chart1")
        # Should be rounded to 1.57
        assert "1.57" in result

    def test_tooltip_callback_present(self) -> None:
        """Test that tooltip callback is present."""
        result = create_chartjs_config([1.5] * 1440, "chart1")
        assert "tooltip:" in result
        assert "callbacks:" in result
        assert "title: function(context)" in result

    def test_zero_values(self) -> None:
        """Test handling of zero values."""
        result = create_chartjs_config([0.0] * 1440, "chart1")
        assert "0.0" in result or "0" in result
        # Should not have negative values
        assert "-" not in result.split("data: [")[1].split("]")[0]

    def test_high_values(self) -> None:
        """Test handling of high MET values."""
        result = create_chartjs_config([5.9] * 1440, "chart1")
        assert "5.9" in result

    def test_varying_values(self) -> None:
        """Test with varying MET values throughout the day."""
        items = []
        # Simulate a day: low at night, high during day
        for hour in range(24):
            for _minute in range(60):
                if 6 <= hour <= 22:
                    items.append(3.0)  # Active during day
                else:
                    items.append(1.0)  # Resting at night
        result = create_chartjs_config(items, "chart1")
        # Should have both 1.0 and 3.0 in the data
        assert "1.0" in result
        assert "3.0" in result
