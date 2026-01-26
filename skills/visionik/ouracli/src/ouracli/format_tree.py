"""Tree formatting for Oura data."""

from typing import Any

from ouracli.charts_ascii import create_ascii_bar_chart, create_heartrate_bar_chart_ascii
from ouracli.format_utils import (
    EXCLUDE_FIELDS,
    calculate_max_position,
    humanize_key,
    sort_dict_keys,
)


def format_tree(
    data: Any, indent: int = 0, parent_is_dict: bool = False, max_position: int | None = None
) -> str:
    """
    Format data as tree structure with human-friendly formatting.

    Args:
        data: Data to format
        indent: Current indentation level
        parent_is_dict: Whether parent container is a dict (for alignment)
        max_position: Maximum position (calculated once for entire structure)

    Returns:
        Formatted string
    """
    # Calculate max position once at the top level
    if max_position is None:
        max_position = calculate_max_position(data)

    lines: list[str] = []
    prefix = "  " * indent

    if isinstance(data, dict):
        # Sort keys with priority fields first
        sorted_keys = sort_dict_keys(data)

        for key in sorted_keys:
            # Skip excluded fields
            if key in EXCLUDE_FIELDS:
                continue

            value = data[key]
            human_key = humanize_key(key)

            if isinstance(value, (dict, list)):
                # Skip empty lists/dicts
                if (isinstance(value, list) and not value) or (
                    isinstance(value, dict) and not value
                ):
                    continue

                # Special handling for MET data with items list
                if key == "met" and isinstance(value, dict) and "items" in value:
                    lines.append(f"{prefix}{human_key}")
                    # Show interval
                    if "interval" in value:
                        interval_indent = "  " * (indent + 1)
                        interval_pos = len(interval_indent) + len("Interval")
                        interval_dots = max_position - interval_pos + 3
                        if interval_dots < 3:
                            interval_dots = 3
                        interval_padding = " " + ("." * interval_dots)
                        lines.append(
                            f"{interval_indent}Interval{interval_padding} {value['interval']}"
                        )

                    # Create bar chart from items
                    if value["items"]:
                        chart_indent = "  " * (indent + 1)
                        lines.append(f"{chart_indent}Activity Chart:")
                        chart = create_ascii_bar_chart(value["items"])
                        # Indent each line of the chart
                        chart_indent_2 = "  " * (indent + 2)
                        for chart_line in chart.split("\n"):
                            lines.append(f"{chart_indent_2}{chart_line}")
                # Special handling for heartrate time-series data
                elif (
                    key == "heartrate"
                    and isinstance(value, list)
                    and value
                    and isinstance(value[0], dict)
                    and "bpm" in value[0]
                ):
                    from datetime import datetime

                    lines.append(f"{prefix}{human_key}")
                    # Group by day
                    by_day_hr: dict[str, list] = {}
                    for reading in value:
                        timestamp_str = reading.get("timestamp", "")
                        if timestamp_str:
                            try:
                                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                                day_key = dt.strftime("%Y-%m-%d")
                                if day_key not in by_day_hr:
                                    by_day_hr[day_key] = []
                                by_day_hr[day_key].append(reading)
                            except (ValueError, AttributeError):
                                continue

                    # Display chart for each day
                    for day in sorted(by_day_hr.keys()):
                        day_data = by_day_hr[day]
                        chart_indent = "  " * (indent + 1)
                        lines.append(f"{chart_indent}{day}")
                        lines.append(f"{chart_indent}  Heart Rate Chart:")
                        chart = create_heartrate_bar_chart_ascii(day_data)
                        chart_indent_2 = "  " * (indent + 3)
                        for chart_line in chart.split("\n"):
                            lines.append(f"{chart_indent_2}{chart_line}")
                else:
                    lines.append(f"{prefix}{human_key}")
                    lines.append(
                        format_tree(
                            value, indent + 1, parent_is_dict=True, max_position=max_position
                        )
                    )
            else:
                # Align simple values with dots (minimum 3 dots, space before dots)
                # Target: max_position + space + 3 dots
                # Current: indent_chars + key_len
                # Dots needed: max_position - current + 3
                indent_chars = len(prefix)
                current_pos = indent_chars + len(human_key)
                dots_needed = max_position - current_pos + 3
                if dots_needed < 3:
                    dots_needed = 3
                padding = " " + ("." * dots_needed)
                lines.append(f"{prefix}{human_key}{padding} {value}")

    elif isinstance(data, list):
        # Check if this is heart rate time-series data
        if data and isinstance(data[0], dict) and "bpm" in data[0] and "timestamp" in data[0]:
            # Group heart rate data by day
            from datetime import datetime

            by_day: dict[str, list] = {}
            for reading in data:
                timestamp_str = reading.get("timestamp", "")
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        day_key = dt.strftime("%Y-%m-%d")
                        if day_key not in by_day:
                            by_day[day_key] = []
                        by_day[day_key].append(reading)
                    except (ValueError, AttributeError):
                        continue

            # Sort days and display chart for each day
            for day in sorted(by_day.keys()):
                day_data = by_day[day]
                lines.append(f"{prefix}{day}")
                lines.append(f"{prefix}  Heart Rate Chart:")
                chart = create_heartrate_bar_chart_ascii(day_data)
                # Indent each line of the chart
                chart_indent = "  " * (indent + 2)
                for chart_line in chart.split("\n"):
                    lines.append(f"{chart_indent}{chart_line}")
                lines.append("")  # Blank line between days
        else:
            for _i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    # Don't show array indices in human-readable output
                    lines.append(
                        format_tree(item, indent, parent_is_dict=False, max_position=max_position)
                    )
                else:
                    lines.append(f"{prefix}{item}")
    else:
        lines.append(f"{prefix}{data}")

    return "\n".join(lines)
