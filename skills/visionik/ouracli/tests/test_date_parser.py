"""Tests for date_parser module."""

from datetime import datetime, timedelta

import pytest

from ouracli.date_parser import parse_date_range


class TestParseDateRange:
    """Tests for parse_date_range function."""

    def test_today(self) -> None:
        """Test parsing 'today'."""
        start, end = parse_date_range("today")
        today = datetime.now().date().strftime("%Y-%m-%d")
        assert start == today
        assert end == today

    def test_yesterday(self) -> None:
        """Test parsing 'yesterday'."""
        start, end = parse_date_range("yesterday")
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert start == yesterday
        assert end == yesterday

    def test_n_days(self) -> None:
        """Test parsing 'n days'."""
        start, end = parse_date_range("7 days")
        today = datetime.now().date()
        expected_start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        expected_end = today.strftime("%Y-%m-%d")
        assert start == expected_start
        assert end == expected_end

    def test_single_day(self) -> None:
        """Test parsing '1 day'."""
        start, end = parse_date_range("1 day")
        today = datetime.now().date().strftime("%Y-%m-%d")
        assert start == today
        assert end == today

    def test_n_weeks(self) -> None:
        """Test parsing 'n weeks'."""
        start, end = parse_date_range("2 weeks")
        today = datetime.now().date()
        expected_start = (today - timedelta(weeks=2)).strftime("%Y-%m-%d")
        expected_end = today.strftime("%Y-%m-%d")
        assert start == expected_start
        assert end == expected_end

    def test_n_months(self) -> None:
        """Test parsing 'n months' (approximate)."""
        start, end = parse_date_range("1 month")
        today = datetime.now().date()
        expected_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        expected_end = today.strftime("%Y-%m-%d")
        assert start == expected_start
        assert end == expected_end

    def test_start_date_plus_days(self) -> None:
        """Test parsing 'YYYY-MM-DD + n days'."""
        start, end = parse_date_range("2024-01-01 7 days")
        assert start == "2024-01-01"
        assert end == "2024-01-08"

    def test_start_date_plus_weeks(self) -> None:
        """Test parsing 'YYYY-MM-DD + n weeks'."""
        start, end = parse_date_range("2024-01-01 2 weeks")
        assert start == "2024-01-01"
        assert end == "2024-01-15"

    def test_direct_date(self) -> None:
        """Test parsing direct date 'YYYY-MM-DD'."""
        start, end = parse_date_range("2024-01-15")
        assert start == "2024-01-15"
        assert end == "2024-01-15"

    def test_invalid_spec(self) -> None:
        """Test invalid date specification."""
        with pytest.raises(ValueError, match="Invalid date specification"):
            parse_date_range("invalid")

    def test_case_insensitive(self) -> None:
        """Test case insensitive parsing."""
        start1, end1 = parse_date_range("TODAY")
        start2, end2 = parse_date_range("today")
        assert start1 == start2
        assert end1 == end2
