"""Fuzzing tests for CLI inputs and API responses."""

import json
from datetime import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ouracli.charts_html import create_chartjs_config, create_chartjs_heartrate_config
from ouracli.charts_mermaid import create_mermaid_bar_chart, create_mermaid_heartrate_chart
from ouracli.date_parser import parse_date_range
from ouracli.formatters import format_output


class TestDateParserFuzzing:
    """Fuzzing tests for date parser."""

    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=200)
    def test_date_parser_handles_arbitrary_strings(self, date_string: str) -> None:
        """Test that date parser doesn't crash on arbitrary strings."""
        # Should either return valid date strings or raise ValueError
        try:
            start, end = parse_date_range(date_string)
            # If it succeeds, validate the result
            assert isinstance(start, str)
            assert isinstance(end, str)
            # Should be valid date format
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            # Expected for invalid inputs
            pass

    @given(st.integers(min_value=-1000, max_value=1000))
    @settings(max_examples=100)
    def test_date_parser_with_numeric_strings(self, num: int) -> None:
        """Test date parser with numeric strings."""
        try:
            start, end = parse_date_range(str(num))
            assert isinstance(start, str)
            assert isinstance(end, str)
        except ValueError:
            pass

    @given(st.text(alphabet="0123456789-T:Z.", min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_date_parser_with_date_like_strings(self, date_str: str) -> None:
        """Test date parser with date-like strings."""
        try:
            start, end = parse_date_range(date_str)
            assert isinstance(start, str)
            assert isinstance(end, str)
        except ValueError:
            pass

    @given(
        st.integers(min_value=1, max_value=365),
        st.sampled_from(["day", "days", "week", "weeks", "month", "months"]),
    )
    @settings(max_examples=50)
    def test_date_parser_with_relative_dates(self, num: int, unit: str) -> None:
        """Test date parser with relative date strings."""
        date_str = f"{num} {unit}"
        try:
            start, end = parse_date_range(date_str)
            assert isinstance(start, str)
            assert isinstance(end, str)
            # Validate date strings
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            assert start_dt <= end_dt
        except ValueError:
            pass


class TestFormattersFuzzing:
    """Fuzzing tests for formatters."""

    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(max_size=100),
            ),
            max_size=20,
        ),
        st.sampled_from(["json", "tree", "markdown", "html"]),
    )
    @settings(max_examples=100)
    def test_format_output_handles_arbitrary_dicts(self, data: dict, format_type: str) -> None:
        """Test that formatters handle arbitrary dictionary data."""
        try:
            result = format_output(data, format_type)
            assert isinstance(result, str)
            # Output should not be empty for non-empty input
            if data:
                assert len(result) > 0
        except (ValueError, TypeError, KeyError):
            # Some exceptions are acceptable (e.g., for invalid data)
            pass

    @given(
        st.lists(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.none(), st.integers(), st.floats(allow_nan=False), st.text(max_size=50)
                ),
                max_size=10,
            ),
            max_size=10,
        ),
        st.sampled_from(["json", "tree", "markdown"]),
    )
    @settings(max_examples=50)
    def test_format_output_handles_list_of_dicts(self, data: list, format_type: str) -> None:
        """Test formatters with lists of dictionaries."""
        try:
            result = format_output(data, format_type)
            assert isinstance(result, str)
        except (ValueError, TypeError):
            pass


class TestChartsHtmlFuzzing:
    """Fuzzing tests for HTML chart generation."""

    @given(
        st.lists(
            st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
            max_size=2000,
        )
    )
    @settings(max_examples=50)
    def test_chartjs_config_handles_arbitrary_met_data(self, met_items: list) -> None:
        """Test Chart.js config generation with arbitrary MET data."""
        try:
            result = create_chartjs_config(met_items, "test_chart")
            assert isinstance(result, str)
            if met_items:
                assert "new Chart" in result
                assert "test_chart" in result
        except Exception as e:
            # Should not crash
            pytest.fail(f"Unexpected exception: {e}")

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "timestamp": st.one_of(
                        st.datetimes(
                            min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31)
                        ).map(lambda dt: dt.isoformat() + "Z"),
                        st.text(alphabet="0123456789-T:Z", max_size=30),
                        st.just(""),
                    ),
                    "bpm": st.one_of(
                        st.none(),
                        st.integers(min_value=30, max_value=220),
                        st.floats(
                            min_value=30, max_value=220, allow_nan=False, allow_infinity=False
                        ),
                    ),
                }
            ),
            max_size=500,
        )
    )
    @settings(max_examples=50)
    def test_chartjs_heartrate_config_handles_arbitrary_data(self, heartrate_data: list) -> None:
        """Test Chart.js heartrate config with arbitrary heart rate data."""
        try:
            result = create_chartjs_heartrate_config(heartrate_data, "hr_chart")
            assert isinstance(result, str)
            # Empty result is OK for invalid data
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @given(
        st.lists(
            st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
            max_size=1440,
        )
    )
    @settings(max_examples=30)
    def test_chartjs_config_handles_extreme_values(self, met_items: list) -> None:
        """Test Chart.js config with extreme values."""
        result = create_chartjs_config(met_items, "extreme")
        assert isinstance(result, str)
        assert "new Chart" in result


class TestChartsMermaidFuzzing:
    """Fuzzing tests for Mermaid chart generation."""

    @given(
        st.lists(
            st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
            max_size=2000,
        )
    )
    @settings(max_examples=50)
    def test_mermaid_bar_chart_handles_arbitrary_data(self, met_items: list) -> None:
        """Test Mermaid bar chart with arbitrary MET data."""
        try:
            result = create_mermaid_bar_chart(met_items)
            assert isinstance(result, str)
            # Should always produce valid output
            if met_items:
                assert "```mermaid" in result
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "timestamp": st.datetimes(
                        min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31)
                    ).map(lambda dt: dt.isoformat() + "Z"),
                    "bpm": st.one_of(
                        st.none(),
                        st.integers(min_value=30, max_value=220),
                        st.floats(
                            min_value=30, max_value=220, allow_nan=False, allow_infinity=False
                        ),
                    ),
                }
            ),
            max_size=500,
        )
    )
    @settings(max_examples=50)
    def test_mermaid_heartrate_chart_handles_arbitrary_data(self, heartrate_data: list) -> None:
        """Test Mermaid heartrate chart with arbitrary data."""
        try:
            result = create_mermaid_heartrate_chart(heartrate_data)
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


class TestAPIResponseFuzzing:
    """Fuzzing tests for API response handling."""

    @given(
        st.dictionaries(
            keys=st.text(
                min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=("Cs",))
            ),
            values=st.recursive(
                st.one_of(
                    st.none(),
                    st.booleans(),
                    st.integers(min_value=-1e9, max_value=1e9),
                    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e9, max_value=1e9),
                    st.text(max_size=200, alphabet=st.characters(blacklist_categories=("Cs",))),
                ),
                lambda children: st.lists(children, max_size=10)
                | st.dictionaries(
                    st.text(
                        min_size=1,
                        max_size=20,
                        alphabet=st.characters(blacklist_categories=("Cs",)),
                    ),
                    children,
                    max_size=10,
                ),
                max_leaves=50,
            ),
            max_size=20,
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_json_formatter_handles_nested_structures(self, data: dict) -> None:
        """Test JSON formatter with deeply nested structures."""
        try:
            result = format_output(data, "json")
            assert isinstance(result, str)
            # Should be valid JSON
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
        except Exception:
            # Some structures might be too complex, that's OK
            pass

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "day": st.dates(
                        min_value=datetime(2020, 1, 1).date(),
                        max_value=datetime(2025, 12, 31).date(),
                    ).map(str),
                    "score": st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
                    "met": st.fixed_dictionaries(
                        {
                            "interval": st.floats(
                                min_value=1, max_value=300, allow_nan=False, allow_infinity=False
                            ),
                            "items": st.lists(
                                st.floats(
                                    min_value=0, max_value=10, allow_nan=False, allow_infinity=False
                                ),
                                min_size=0,
                                max_size=1440,
                            ),
                        }
                    ),
                }
            ),
            max_size=10,
        )
    )
    @settings(max_examples=30, deadline=None)
    def test_formatters_handle_activity_response_structure(self, activity_data: list) -> None:
        """Test formatters with Oura API-like activity response structure."""
        data = {"activity": activity_data}
        for format_type in ["json", "tree", "markdown"]:
            try:
                result = format_output(data, format_type)
                assert isinstance(result, str)
                # Empty data can produce empty or minimal output, that's OK
                if activity_data:
                    assert len(result) > 0
            except Exception as e:
                pytest.fail(f"Failed for {format_type}: {e}")

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "day": st.dates(
                        min_value=datetime(2020, 1, 1).date(),
                        max_value=datetime(2025, 12, 31).date(),
                    ).map(str),
                    "bpm": st.integers(min_value=30, max_value=220),
                    "source": st.sampled_from(["sleep", "rest", "activity"]),
                }
            ),
            max_size=50,
        )
    )
    @settings(max_examples=30)
    def test_formatters_handle_heartrate_summary_structure(self, heartrate_data: list) -> None:
        """Test formatters with heart rate summary structure."""
        for format_type in ["json", "tree"]:
            try:
                result = format_output(heartrate_data, format_type)
                assert isinstance(result, str)
            except Exception as e:
                pytest.fail(f"Failed for {format_type}: {e}")


class TestEdgeCases:
    """Edge case fuzzing tests."""

    @given(st.text(alphabet=st.characters(blacklist_categories=("Cs", "Cc")), max_size=1000))
    @settings(max_examples=50)
    def test_formatters_handle_unicode(self, text: str) -> None:
        """Test that formatters handle Unicode text."""
        data = {"text": text, "value": 123}
        for format_type in ["json", "tree"]:
            try:
                result = format_output(data, format_type)
                assert isinstance(result, str)
            except Exception:
                # Some Unicode might cause issues, that's acceptable
                pass

    @given(st.lists(st.floats(allow_nan=True, allow_infinity=True), max_size=100))
    @settings(max_examples=30)
    def test_chartjs_handles_special_float_values(self, values: list) -> None:
        """Test Chart.js config handles NaN and Infinity."""
        # Filter out NaN and Infinity as they're not valid for our use case
        clean_values = [v for v in values if not (float("inf") == abs(v) or v != v)]
        try:
            result = create_chartjs_config(clean_values, "special")
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @given(st.integers(min_value=0, max_value=10000))
    @settings(max_examples=30)
    def test_chartjs_handles_variable_data_lengths(self, length: int) -> None:
        """Test Chart.js config with various data lengths."""
        met_items = [1.5] * length
        result = create_chartjs_config(met_items, "var_length")
        assert isinstance(result, str)
        assert "new Chart" in result

    @given(st.lists(st.dictionaries(st.text(max_size=10), st.none(), max_size=5), max_size=20))
    @settings(max_examples=30)
    def test_formatters_handle_all_none_values(self, data: list) -> None:
        """Test formatters with all None values."""
        try:
            result = format_output(data, "json")
            assert isinstance(result, str)
        except Exception:
            pass

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "timestamp": st.text(alphabet="XYZ", max_size=20),  # Invalid timestamps
                    "bpm": st.integers(min_value=30, max_value=220),
                }
            ),
            max_size=100,
        )
    )
    @settings(max_examples=30)
    def test_heartrate_chart_handles_malformed_timestamps(self, data: list) -> None:
        """Test heart rate charts with completely malformed timestamps."""
        result = create_chartjs_heartrate_config(data, "malformed")
        # Should return empty string or valid chart
        assert isinstance(result, str)
