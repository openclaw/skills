"""Markdown formatting for Oura data."""

from typing import Any

from ouracli.charts_mermaid import create_mermaid_bar_chart, create_mermaid_heartrate_chart
from ouracli.format_utils import EXCLUDE_FIELDS, humanize_key, sort_dict_keys


def format_markdown_item(data: Any, heading_level: int = 3) -> str:
    """
    Format a single item as markdown with proper heading hierarchy.
    Uses tables for simple key-value pairs.

    Args:
        data: Data to format
        heading_level: Current heading level (3 for ### subsections)

    Returns:
        Formatted markdown string
    """
    lines: list[str] = []

    if isinstance(data, dict):
        sorted_keys = sort_dict_keys(data)

        # Separate simple key-values from complex nested structures
        simple_kvs = []
        complex_items: list[tuple[str, dict[Any, Any] | list[Any], str, str]] = []

        for key in sorted_keys:
            if key in EXCLUDE_FIELDS:
                continue

            value = data[key]
            human_key = humanize_key(key)

            if isinstance(value, dict):
                # Special handling for MET data
                if key == "met" and "items" in value:
                    complex_items.append((key, value, human_key, "met"))
                # Contributors and other nested dicts
                elif not any(isinstance(v, (dict, list)) for v in value.values()):
                    # Flat dict - use as subsection with table
                    complex_items.append((key, value, human_key, "flat_dict"))
                else:
                    # Complex nested structure
                    complex_items.append((key, value, human_key, "complex"))
            elif isinstance(value, list):
                # Check if this is heart rate time-series data
                if (
                    value
                    and isinstance(value[0], dict)
                    and "bpm" in value[0]
                    and "timestamp" in value[0]
                ):
                    complex_items.append((key, value, human_key, "heartrate"))
                # Lists of complex items get their own subsection
                elif value and isinstance(value[0], dict):
                    complex_items.append((key, value, human_key, "complex_list"))
                else:
                    # Simple list values - treat as simple kv
                    simple_kvs.append((human_key, ", ".join(map(str, value))))
            else:
                # Simple key-value pairs
                simple_kvs.append((human_key, value))

        # Render simple key-values as table
        if simple_kvs:
            lines.append("| Field | Value |")
            lines.append("|-------|-------|")
            for k, v in simple_kvs:
                lines.append(f"| {k} | {v} |")
            lines.append("")

        # Render complex items as subsections
        for _key, value, human_key, item_type in complex_items:
            if item_type == "met" and isinstance(value, dict):
                lines.append(f"\n{'#' * heading_level} {human_key}\n")
                if "interval" in value:
                    lines.append(f"**Interval:** {value['interval']} seconds\n")
                if value["items"]:
                    lines.append("**Activity Chart:**\n")
                    chart = create_mermaid_bar_chart(value["items"])  # type: ignore[arg-type]
                    lines.append(chart)
                    lines.append("")
            elif item_type == "flat_dict" and isinstance(value, dict):
                lines.append(f"\n{'#' * heading_level} {human_key}\n")
                # Render flat dict as table
                lines.append("| Field | Value |")
                lines.append("|-------|-------|")
                for subkey, subvalue in value.items():
                    if subkey not in EXCLUDE_FIELDS:
                        sub_human_key = humanize_key(subkey)
                        lines.append(f"| {sub_human_key} | {subvalue} |")
                lines.append("")
            elif item_type == "complex":
                lines.append(f"\n{'#' * heading_level} {human_key}\n")
                lines.append(format_markdown_item(value, heading_level + 1))  # type: ignore[arg-type]
            elif item_type == "heartrate" and isinstance(value, list):
                lines.append(f"\n{'#' * heading_level} {human_key}\n")
                lines.append("**Heart Rate Chart:**\n")
                # Cast value to list[dict] for type checker
                chart = create_mermaid_heartrate_chart(value)  # type: ignore[arg-type]
                lines.append(chart)
                lines.append("")
            elif item_type == "complex_list" and isinstance(value, list):
                lines.append(f"\n{'#' * heading_level} {human_key}\n")
                for item in value:
                    lines.append(format_markdown_item(item, heading_level + 1))

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(format_markdown_item(item, heading_level))
            else:
                lines.append(f"- {item}")
    else:
        lines.append(str(data))

    return "\n".join(lines)


def format_markdown(data: Any, title: str | None = None) -> str:
    """
    Format data as Markdown with proper heading hierarchy.
    # Top-level category (Activity, Sleep, etc.)
    ## Date/Day
    ### Subsections (Contributors, MET, etc.)

    Args:
        data: Data to format
        title: Optional title for top-level heading when data is a list

    Returns:
        Markdown formatted string
    """
    lines: list[str] = []

    if isinstance(data, dict):
        # If dict contains lists of data by category (e.g., activity, sleep, etc.)
        if all(isinstance(v, list) for v in data.values()):
            for key, values in data.items():
                section_title = key.replace("_", " ").title()
                lines.append(f"# {section_title}\n")

                if not values:
                    lines.append("*No data*\n")
                    continue

                # Format each item in the list
                for _i, item in enumerate(values):
                    if isinstance(item, dict):
                        # Add day header if available
                        if "day" in item:
                            lines.append(f"\n## {item['day']}\n")
                        lines.append(format_markdown_item(item, heading_level=3))
                        lines.append("")  # Blank line between items
                    else:
                        lines.append(f"- {item}")
        else:
            # Single dict - format as section
            lines.append("# Data\n")
            lines.append(format_markdown_item(data, heading_level=2))

    elif isinstance(data, list):
        if not data:
            lines.append("*No data*")
        else:
            # Check if this is heart rate time-series data
            if data and isinstance(data[0], dict) and "bpm" in data[0] and "timestamp" in data[0]:
                # Group heart rate data by day
                from datetime import datetime

                if title:
                    lines.append(f"# {title}\n")

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

                # Create chart for each day
                for day in sorted(by_day.keys()):
                    day_data = by_day[day]
                    lines.append(f"## {day}\n")
                    lines.append("**Heart Rate Chart:**\n")
                    chart = create_mermaid_heartrate_chart(day_data)
                    lines.append(chart)
                    lines.append("")
            else:
                # Add title if provided
                if title:
                    lines.append(f"# {title}\n")

                for item in data:
                    if isinstance(item, dict):
                        if "day" in item:
                            lines.append(f"\n## {item['day']}\n")
                        lines.append(format_markdown_item(item, heading_level=3))
                        lines.append("")  # Blank line
                    else:
                        lines.append(f"- {item}")
    else:
        lines.append(str(data))

    return "\n".join(lines)
