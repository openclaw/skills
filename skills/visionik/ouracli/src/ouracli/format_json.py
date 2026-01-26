"""JSON formatting for Oura data."""

import json
from typing import Any


def format_json(data: Any) -> str:
    """
    Format data as JSON with MET items arrays on single lines.

    Args:
        data: Data to format

    Returns:
        JSON formatted string
    """
    # First pass: serialize to compact JSON to get items arrays
    compact = json.dumps(data, default=str)
    parsed = json.loads(compact)

    # Format with custom handling for met.items
    def custom_format(obj: Any, indent_level: int = 0) -> str:
        indent = "  " * indent_level
        next_indent = "  " * (indent_level + 1)

        if isinstance(obj, dict):
            # Check if this is a met dict with items
            if "items" in obj and "interval" in obj:
                # Special formatting for MET data
                lines = []
                lines.append("{")
                for i, (k, v) in enumerate(obj.items()):
                    comma = "," if i < len(obj) - 1 else ""
                    if k == "items" and isinstance(v, list):
                        # Format items array on single line
                        items_str = json.dumps(v)
                        lines.append(f'{next_indent}"{k}": {items_str}{comma}')
                    else:
                        lines.append(f'{next_indent}"{k}": {json.dumps(v, default=str)}{comma}')
                lines.append(f"{indent}}}")
                return "\n".join(lines)
            # Regular dict formatting
            if not obj:
                return "{}"
            lines = []
            lines.append("{")
            items = list(obj.items())
            for i, (k, v) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                formatted_value = custom_format(v, indent_level + 1)
                # Check if value is multiline
                if "\n" in formatted_value:
                    lines.append(f'{next_indent}"{k}": {formatted_value}{comma}')
                else:
                    lines.append(f'{next_indent}"{k}": {formatted_value}{comma}')
            lines.append(f"{indent}}}")
            return "\n".join(lines)
        if isinstance(obj, list):
            if not obj:
                return "[]"
            # Check if all items are dicts (like activity records)
            if all(isinstance(item, dict) for item in obj):
                lines = []
                lines.append("[")
                for i, item in enumerate(obj):
                    comma = "," if i < len(obj) - 1 else ""
                    formatted_item = custom_format(item, indent_level + 1)
                    lines.append(f"{next_indent}{formatted_item}{comma}")
                lines.append(f"{indent}]")
                return "\n".join(lines)
            # Simple list - keep on one line
            return json.dumps(obj, default=str)
        return json.dumps(obj, default=str)

    return custom_format(parsed)
