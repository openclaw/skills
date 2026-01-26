"""Output formatters for Oura data."""

from typing import Any

# Import and re-export all formatter functions
from ouracli.charts_ascii import create_ascii_bar_chart, create_heartrate_bar_chart_ascii
from ouracli.charts_html import create_chartjs_config, create_chartjs_heartrate_config
from ouracli.charts_mermaid import create_mermaid_bar_chart, create_mermaid_heartrate_chart
from ouracli.format_dataframe import format_dataframe
from ouracli.format_html import format_html
from ouracli.format_json import format_json
from ouracli.format_markdown import format_markdown, format_markdown_item
from ouracli.format_tree import format_tree
from ouracli.format_utils import (
    EXCLUDE_FIELDS,
    FIELD_ORDER,
    FIELD_ORDER_END,
    calculate_max_position,
    humanize_key,
    reorganize_by_day,
    sort_dict_keys,
)

# Re-export for backwards compatibility
__all__ = [
    "create_ascii_bar_chart",
    "create_heartrate_bar_chart_ascii",
    "create_chartjs_config",
    "create_chartjs_heartrate_config",
    "create_mermaid_bar_chart",
    "create_mermaid_heartrate_chart",
    "format_dataframe",
    "format_html",
    "format_json",
    "format_markdown",
    "format_markdown_item",
    "format_tree",
    "format_output",
    "EXCLUDE_FIELDS",
    "FIELD_ORDER",
    "FIELD_ORDER_END",
    "calculate_max_position",
    "humanize_key",
    "reorganize_by_day",
    "sort_dict_keys",
]


def format_output(data: Any, format_type: str = "tree", by_day: bool = False) -> str:
    """
    Format data according to specified format type.

    Args:
        data: Data to format
        format_type: Output format (tree, json, dataframe, markdown, html)
        by_day: If True and data is a dict of methods, reorganize by day first

    Returns:
        Formatted string
    """
    # Reorganize by day if requested and data structure matches
    if by_day and isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        data = reorganize_by_day(data)

    if format_type == "json":
        return format_json(data)
    if format_type == "dataframe":
        return format_dataframe(data)
    if format_type == "markdown":
        return format_markdown(data)
    if format_type == "html":
        return format_html(data)
    if format_type == "tree":
        return format_tree(data)
    raise ValueError(f"Unknown format type: {format_type}")
