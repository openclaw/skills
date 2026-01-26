"""HTML formatting for Oura data."""

from typing import Any

from ouracli.charts_html import create_chartjs_config, create_chartjs_heartrate_config
from ouracli.format_utils import EXCLUDE_FIELDS, humanize_key, sort_dict_keys


def format_html(data: Any, title: str | None = None) -> str:
    """
    Format data as HTML with Chart.js visualizations.

    Args:
        data: Data to format
        title: Optional title for the page

    Returns:
        Complete HTML document as string
    """
    chart_configs = []
    chart_counter = [0]  # Use list to allow mutation in nested function

    def format_html_item(item_data: Any, level: int = 2) -> str:
        """Format a single data item as HTML."""
        html = []

        if isinstance(item_data, dict):
            sorted_keys = sort_dict_keys(item_data)

            # Separate simple and complex items
            simple_kvs = []
            complex_items = []

            for key in sorted_keys:
                if key in EXCLUDE_FIELDS:
                    continue

                value = item_data[key]
                human_key = humanize_key(key)

                if isinstance(value, dict):
                    if key == "met" and "items" in value:
                        chart_counter[0] += 1
                        chart_id = f"chart{chart_counter[0]}"
                        chart_configs.append(create_chartjs_config(value["items"], chart_id))
                        interval = value.get("interval", "N/A")
                        interval_p = f"<p><strong>Interval:</strong> {interval} seconds</p>"
                        chart_div = (
                            f'<div style="height: 400px; margin: 20px 0;">'
                            f'<canvas id="{chart_id}"></canvas></div>'
                        )
                        complex_items.append(
                            (f"<h{level}>{human_key}</h{level}>", interval_p + chart_div)
                        )
                    elif not any(isinstance(v, (dict, list)) for v in value.values()):
                        # Flat dict - render as table
                        table_rows = []
                        for subkey, subvalue in value.items():
                            if subkey not in EXCLUDE_FIELDS:
                                sub_human_key = humanize_key(subkey)
                                table_rows.append(
                                    f"<tr><td>{sub_human_key}</td><td>{subvalue}</td></tr>"
                                )
                        complex_items.append(
                            (
                                f"<h{level}>{human_key}</h{level}>",
                                "<table>" + "".join(table_rows) + "</table>",
                            )
                        )
                    else:
                        complex_items.append(
                            (
                                f"<h{level}>{human_key}</h{level}>",
                                format_html_item(value, level + 1),
                            )
                        )
                elif isinstance(value, list):
                    # Check if this is heart rate time-series data
                    if (
                        value
                        and isinstance(value[0], dict)
                        and "bpm" in value[0]
                        and "timestamp" in value[0]
                    ):
                        from datetime import datetime

                        # Group by day
                        by_day: dict[str, list] = {}
                        for reading in value:
                            timestamp_str = reading.get("timestamp", "")
                            if timestamp_str:
                                try:
                                    dt = datetime.fromisoformat(
                                        timestamp_str.replace("Z", "+00:00")
                                    )
                                    day_key = dt.strftime("%Y-%m-%d")
                                    if day_key not in by_day:
                                        by_day[day_key] = []
                                    by_day[day_key].append(reading)
                                except (ValueError, AttributeError):
                                    continue

                        # Create charts grouped by day
                        charts_html = []
                        for day in sorted(by_day.keys()):
                            day_data = by_day[day]
                            chart_counter[0] += 1
                            chart_id = f"chart{chart_counter[0]}"
                            chart_config = create_chartjs_heartrate_config(day_data, chart_id)
                            if chart_config:
                                chart_configs.append(chart_config)
                                charts_html.append(f"<h{level+1}>{day}</h{level+1}>")
                                chart_div = (
                                    f'<div style="height: 400px; margin: 20px 0;">'
                                    f'<canvas id="{chart_id}"></canvas></div>'
                                )
                                charts_html.append(chart_div)

                        if charts_html:
                            complex_items.append(
                                (f"<h{level}>{human_key}</h{level}>", "\n".join(charts_html))
                            )
                    elif value and isinstance(value[0], dict):
                        items_html = "".join([format_html_item(item, level + 1) for item in value])
                        complex_items.append((f"<h{level}>{human_key}</h{level}>", items_html))
                    else:
                        simple_kvs.append((human_key, ", ".join(map(str, value))))
                else:
                    simple_kvs.append((human_key, value))

            # Render simple KVs as table
            if simple_kvs:
                html.append("<table>")
                for k, v in simple_kvs:
                    html.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
                html.append("</table>")

            # Render complex items
            for heading, content in complex_items:
                html.append(heading)
                html.append(content)

        return "\n".join(html)

    # Build HTML document
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append('<html lang="en">')
    html_parts.append("<head>")
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'<title>{title or "Oura Data"}</title>')
    html_parts.append(
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'
    )
    html_parts.append("<style>")
    html_parts.append(
        """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                "Helvetica Neue", Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #2E7D32;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #388E3C;
            border-bottom: 2px solid #81C784;
            padding-bottom: 8px;
            margin-top: 30px;
        }
        h3 { color: #43A047; margin-top: 20px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        table td:first-child {
            font-weight: 600;
            color: #555;
            width: 40%;
        }
        table tr:hover {
            background-color: #f9f9f9;
        }
        canvas {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    """
    )
    html_parts.append("</style>")
    html_parts.append("</head>")
    html_parts.append("<body>")

    # Process data
    if isinstance(data, dict):
        if all(isinstance(v, list) for v in data.values()):
            for key, values in data.items():
                section_title = key.replace("_", " ").title()
                html_parts.append(f"<h1>{section_title}</h1>")

                if not values:
                    html_parts.append("<p><em>No data</em></p>")
                    continue

                for item in values:
                    if isinstance(item, dict) and "day" in item:
                        html_parts.append(f'<h2>{item["day"]}</h2>')
                    html_parts.append(format_html_item(item, level=3))
        else:
            html_parts.append("<h1>Data</h1>")
            html_parts.append(format_html_item(data, level=2))
    elif isinstance(data, list):
        # Check if this is heart rate time-series data
        if data and isinstance(data[0], dict) and "bpm" in data[0] and "timestamp" in data[0]:
            from datetime import datetime

            if title:
                html_parts.append(f"<h1>{title}</h1>")

            # Group by day
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
                html_parts.append(f"<h2>{day}</h2>")
                chart_counter[0] += 1
                chart_id = f"chart{chart_counter[0]}"
                chart_config = create_chartjs_heartrate_config(day_data, chart_id)
                if chart_config:
                    chart_configs.append(chart_config)
                    chart_div = (
                        f'<div style="height: 400px; margin: 20px 0;">'
                        f'<canvas id="{chart_id}"></canvas></div>'
                    )
                    html_parts.append(chart_div)
        else:
            if title:
                html_parts.append(f"<h1>{title}</h1>")
            for item in data:
                if isinstance(item, dict) and "day" in item:
                    html_parts.append(f'<h2>{item["day"]}</h2>')
                html_parts.append(format_html_item(item, level=3))

    # Add Chart.js initialization
    if chart_configs:
        html_parts.append("<script>")
        html_parts.append('window.addEventListener("DOMContentLoaded", function() {')
        for config in chart_configs:
            html_parts.append(config)
        html_parts.append("});")
        html_parts.append("</script>")

    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)
