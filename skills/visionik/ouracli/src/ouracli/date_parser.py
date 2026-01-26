"""Date range parsing utilities for flexible date specifications."""

import re
from datetime import datetime, timedelta


def parse_date_range(date_spec: str) -> tuple[str, str]:
    """
    Parse flexible date range specifications into start_date and end_date.

    Supports:
    - today
    - yesterday
    - 1 day, 2 days, n days
    - 1 week, 2 weeks, n weeks
    - 1 month, 2 months, n months
    - YYYY-MM-DD + period (e.g., "2024-01-01 7 days")

    Args:
        date_spec: Date specification string

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format

    Examples:
        >>> parse_date_range("today")
        ('2024-01-01', '2024-01-01')
        >>> parse_date_range("7 days")
        ('2023-12-25', '2024-01-01')
        >>> parse_date_range("2024-01-01 7 days")
        ('2024-01-01', '2024-01-08')
    """
    date_spec = date_spec.strip().lower()
    today = datetime.now().date()

    # Handle "today"
    if date_spec == "today":
        date_str = today.strftime("%Y-%m-%d")
        return (date_str, date_str)

    # Handle "yesterday"
    if date_spec == "yesterday":
        yesterday = today - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        return (date_str, date_str)

    # Handle "n day(s)", "n week(s)", "n month(s)"
    relative_pattern = r"^(\d+)\s+(day|days|week|weeks|month|months)$"
    match = re.match(relative_pattern, date_spec)
    if match:
        n = int(match.group(1))
        unit = match.group(2)

        if unit in ("day", "days"):
            start = today - timedelta(days=n - 1)
        elif unit in ("week", "weeks"):
            start = today - timedelta(weeks=n)
        elif unit in ("month", "months"):
            # Approximate: 30 days per month
            start = today - timedelta(days=n * 30)
        else:
            raise ValueError(f"Unknown unit: {unit}")

        return (start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

    # Handle "YYYY-MM-DD + period"
    start_plus_pattern = r"^(\d{4}-\d{2}-\d{2})\s+(\d+)\s+(day|days|week|weeks|month|months)$"
    match = re.match(start_plus_pattern, date_spec)
    if match:
        start_str = match.group(1)
        n = int(match.group(2))
        unit = match.group(3)

        start = datetime.strptime(start_str, "%Y-%m-%d").date()

        if unit in ("day", "days"):
            end = start + timedelta(days=n)
        elif unit in ("week", "weeks"):
            end = start + timedelta(weeks=n)
        elif unit in ("month", "months"):
            # Approximate: 30 days per month
            end = start + timedelta(days=n * 30)
        else:
            raise ValueError(f"Unknown unit: {unit}")

        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # Handle direct date "YYYY-MM-DD"
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(date_pattern, date_spec):
        return (date_spec, date_spec)

    raise ValueError(f"Invalid date specification: {date_spec}")
