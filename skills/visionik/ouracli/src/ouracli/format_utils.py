"""Core formatting utilities for Oura data."""

from typing import Any

# Fields to exclude from tree output
EXCLUDE_FIELDS = {"id", "timestamp", "class_5_min"}

# Field priority order (fields at top of list appear first)
FIELD_ORDER = [
    "day",
    "date",
    "timestamp",
    "score",
]

# Fields that should appear at the end
FIELD_ORDER_END = [
    "met",
]


def humanize_key(key: str) -> str:
    """
    Convert key to human-readable format.

    - Replace underscores with spaces
    - Capitalize first letter of each word
    - Capitalize abbreviations like REM, SPO2, HRV

    Args:
        key: Original key name

    Returns:
        Humanized key name
    """
    # Replace underscores with spaces
    key = key.replace("_", " ")

    # Capitalize each word
    words = key.split()
    result = []

    for word in words:
        # Special handling for known abbreviations
        upper_word = word.upper()
        if upper_word in {"REM", "SPO2", "HRV", "BMI", "HR", "BPM", "MET", "ID"}:
            result.append(upper_word)
        else:
            # Regular capitalization
            result.append(word.capitalize())

    return " ".join(result)


def sort_dict_keys(d: dict[str, Any]) -> list[str]:
    """
    Sort dictionary keys with priority fields first, then alphabetically, then end fields last.

    Args:
        d: Dictionary to sort

    Returns:
        Sorted list of keys
    """
    keys = list(d.keys())

    # Separate priority, end, and other keys
    priority_keys = []
    end_keys = []
    other_keys = []

    for key in keys:
        if key in FIELD_ORDER:
            priority_keys.append(key)
        elif key in FIELD_ORDER_END:
            end_keys.append(key)
        else:
            other_keys.append(key)

    # Sort priority keys by their order in FIELD_ORDER
    priority_keys.sort(key=lambda k: FIELD_ORDER.index(k) if k in FIELD_ORDER else len(FIELD_ORDER))

    # Sort end keys by their order in FIELD_ORDER_END
    end_keys.sort(
        key=lambda k: FIELD_ORDER_END.index(k) if k in FIELD_ORDER_END else len(FIELD_ORDER_END)
    )

    # Sort other keys alphabetically
    other_keys.sort()

    return priority_keys + other_keys + end_keys


def calculate_max_position(data: Any, indent: int = 0) -> int:
    """
    Calculate the maximum position (indent + key length) across the entire data structure.

    Args:
        data: Data to analyze
        indent: Current indentation level

    Returns:
        Maximum position (indent chars + humanized key length)
    """
    max_pos = 0
    indent_chars = indent * 2  # 2 spaces per indent level

    if isinstance(data, dict):
        for key, value in data.items():
            if key not in EXCLUDE_FIELDS:
                if not isinstance(value, (dict, list)):
                    pos = indent_chars + len(humanize_key(key))
                    max_pos = max(max_pos, pos)
                else:
                    # Recursively check nested structures with increased indent
                    max_pos = max(max_pos, calculate_max_position(value, indent + 1))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                max_pos = max(max_pos, calculate_max_position(item, indent + 1))

    return max_pos


def reorganize_by_day(data: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """
    Reorganize data from {method: [{day: ..., ...}]} to {day: {method: {...}}}.

    Args:
        data: Dictionary with method names as keys and lists of daily data as values

    Returns:
        Dictionary with dates as keys and methods as nested keys
    """
    by_day: dict[str, dict[str, Any]] = {}

    for method, items in data.items():
        if not isinstance(items, list):
            # Handle personal_info which might be a single dict
            if method == "personal_info" and items:
                # Add personal info to a special key
                for day in by_day.values():
                    day["personal_info"] = items[0] if isinstance(items, list) else items
            continue

        # Special handling for heartrate time-series data
        if method == "heartrate" and items and isinstance(items[0], dict) and "bpm" in items[0]:
            from datetime import datetime

            # Group heartrate records by day
            heartrate_by_day: dict[str, list] = {}
            for reading in items:
                timestamp_str = reading.get("timestamp", "")
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        day_key = dt.strftime("%Y-%m-%d")
                        if day_key not in heartrate_by_day:
                            heartrate_by_day[day_key] = []
                        heartrate_by_day[day_key].append(reading)
                    except (ValueError, AttributeError):
                        continue

            # Add grouped heartrate data to each day
            for day_key, day_readings in heartrate_by_day.items():
                if day_key not in by_day:
                    by_day[day_key] = {}
                by_day[day_key][method] = day_readings
            continue

        for item in items:
            if isinstance(item, dict):
                # Get the day field - try different possible field names
                day = item.get("day") or item.get("date") or item.get("summary_date")

                if day:
                    if day not in by_day:
                        by_day[day] = {}
                    by_day[day][method] = item

    # Sort by day (chronologically)
    return dict(sorted(by_day.items()))
