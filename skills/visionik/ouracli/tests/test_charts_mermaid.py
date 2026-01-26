"""Tests for charts_mermaid module."""

from ouracli.charts_mermaid import (
    create_mermaid_bar_chart,
    create_mermaid_heartrate_chart,
)


class TestCreateMermaidBarChart:
    """Tests for create_mermaid_bar_chart function."""

    def test_empty_data(self) -> None:
        """Test with empty MET data."""
        result = create_mermaid_bar_chart([])
        # Empty data still creates a chart (just with no bars)
        assert "```mermaid" in result

    def test_mermaid_format(self) -> None:
        """Test that output uses Mermaid format."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert "```mermaid" in result
        assert "xychart-beta" in result
        assert "```" in result

    def test_title(self) -> None:
        """Test that chart has title."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert "24-Hour MET Activity" in result

    def test_dark_theme(self) -> None:
        """Test that dark theme is applied."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert "'theme':'dark'" in result

    def test_x_axis_labels(self) -> None:
        """Test that X-axis has hour labels."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert '"Hour"' in result
        assert "x-axis" in result

    def test_y_axis_labels(self) -> None:
        """Test that Y-axis has MET label."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert '"Average MET"' in result
        assert "y-axis" in result

    def test_24_hour_labels(self) -> None:
        """Test that there are 24 hour labels."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        # Should have labels for hours 0-23
        assert '"00"' in result
        assert '"12"' in result
        assert '"23"' in result

    def test_hourly_aggregation(self) -> None:
        """Test that data is aggregated by hour."""
        # Create 1440 items with known pattern
        items = []
        for hour in range(24):
            for _minute in range(60):
                items.append(float(hour))  # Each hour has its hour number as value
        result = create_mermaid_bar_chart(items)
        # Should have 24 data points (one per hour)
        # Each hour's value should be the hour number
        assert "[0.0" in result  # Hour 0
        assert "12.0" in result  # Hour 12
        assert "23.0" in result  # Hour 23

    def test_partial_data(self) -> None:
        """Test with partial day data."""
        # Only 100 items
        result = create_mermaid_bar_chart([2.0] * 100)
        assert "```mermaid" in result
        # Should still generate valid chart

    def test_varying_values(self) -> None:
        """Test with varying MET values."""
        items = []
        for hour in range(24):
            for _minute in range(60):
                if 6 <= hour <= 22:
                    items.append(3.5)
                else:
                    items.append(1.0)
        result = create_mermaid_bar_chart(items)
        # Should have both high and low values in output
        assert "3.5" in result
        assert "1.0" in result

    def test_bar_chart_type(self) -> None:
        """Test that chart is bar type."""
        result = create_mermaid_bar_chart([1.5] * 1440)
        assert "bar" in result


class TestCreateMermaidHeartrateChart:
    """Tests for create_mermaid_heartrate_chart function."""

    def test_empty_data(self) -> None:
        """Test with empty heart rate data."""
        result = create_mermaid_heartrate_chart([])
        assert result == "No heart rate data"

    def test_no_valid_bpm(self) -> None:
        """Test with data that has no valid BPM values."""
        data = [
            {"timestamp": "2025-01-01T00:00:00Z", "bpm": None},
            {"timestamp": "2025-01-01T01:00:00Z", "bpm": None},
        ]
        result = create_mermaid_heartrate_chart(data)
        assert result == "No heart rate data"

    def test_mermaid_format(self) -> None:
        """Test that output uses Mermaid format."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert "```mermaid" in result
        assert "xychart-beta" in result
        assert "```" in result

    def test_title(self) -> None:
        """Test that chart has title."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert "24-Hour Heart Rate" in result

    def test_dark_theme(self) -> None:
        """Test that dark theme is applied."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert "'theme':'dark'" in result

    def test_x_axis_labels(self) -> None:
        """Test that X-axis has hour labels."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert '"Hour"' in result
        assert "x-axis" in result

    def test_y_axis_labels(self) -> None:
        """Test that Y-axis has BPM label."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert '"Average BPM"' in result
        assert "y-axis" in result

    def test_24_hour_labels(self) -> None:
        """Test that there are 24 hour labels."""
        # Create data spanning 24 hours
        data = []
        for hour in range(24):
            data.append({"timestamp": f"2025-01-01T{hour:02d}:00:00Z", "bpm": 70})
        result = create_mermaid_heartrate_chart(data)
        assert '"00"' in result
        assert '"12"' in result
        assert '"23"' in result

    def test_hourly_aggregation(self) -> None:
        """Test that BPM values are aggregated by hour."""
        # Create multiple readings per hour
        data = []
        for minute in range(60):
            data.append(
                {
                    "timestamp": f"2025-01-01T12:{minute:02d}:00Z",
                    "bpm": 70 + minute,  # Increasing BPM
                }
            )
        result = create_mermaid_heartrate_chart(data)
        # Hour 12 should have average BPM around 99.5 (70 + 29.5)
        # The actual average is (70 + 129) / 2 = 99.5
        assert "99" in result or "100" in result

    def test_invalid_timestamps_skipped(self) -> None:
        """Test that invalid timestamps are skipped."""
        data = [
            {"timestamp": "invalid", "bpm": 70},
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": 75},
        ]
        result = create_mermaid_heartrate_chart(data)
        # Should still generate output with valid data
        assert "```mermaid" in result
        assert "75" in result

    def test_missing_bpm_skipped(self) -> None:
        """Test that missing BPM values are skipped."""
        data = [
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": None},
            {"timestamp": "2025-01-01T13:00:00Z", "bpm": 75},
        ]
        result = create_mermaid_heartrate_chart(data)
        # Should generate output with valid data only
        assert "```mermaid" in result
        assert "75" in result

    def test_varying_bpm_values(self) -> None:
        """Test with varying BPM values throughout the day."""
        data = []
        for hour in range(24):
            bpm = 80 if 6 <= hour <= 22 else 60
            data.append({"timestamp": f"2025-01-01T{hour:02d}:00:00Z", "bpm": bpm})
        result = create_mermaid_heartrate_chart(data)
        # Should have both high and low values
        assert "80" in result
        assert "60" in result

    def test_bar_chart_type(self) -> None:
        """Test that chart is bar type."""
        data = [{"timestamp": "2025-01-01T12:00:00Z", "bpm": 70}]
        result = create_mermaid_heartrate_chart(data)
        assert "bar" in result

    def test_multiple_readings_same_hour(self) -> None:
        """Test averaging when multiple readings in same hour."""
        data = [
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": 60},
            {"timestamp": "2025-01-01T12:30:00Z", "bpm": 80},
        ]
        result = create_mermaid_heartrate_chart(data)
        # Average should be 70
        assert "70" in result

    def test_rounding(self) -> None:
        """Test that BPM values are properly rounded."""
        data = [
            {"timestamp": "2025-01-01T12:00:00Z", "bpm": 70.4},
            {"timestamp": "2025-01-01T12:30:00Z", "bpm": 70.6},
        ]
        result = create_mermaid_heartrate_chart(data)
        # Average is 70.5, should round to 70 or 71
        assert "70" in result or "71" in result
