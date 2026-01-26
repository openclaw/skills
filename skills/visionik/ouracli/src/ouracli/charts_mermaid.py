"""Mermaid chart generation for markdown output."""


def create_mermaid_heartrate_chart(heartrate_data: list[dict]) -> str:
    """
    Create a Mermaid bar chart from heart rate data.

    Args:
        heartrate_data: List of dicts with 'timestamp' and 'bpm' keys

    Returns:
        Mermaid chart definition as string
    """
    from datetime import datetime

    if not heartrate_data:
        return "No heart rate data"

    # Group into hourly buckets (24 hours)
    hourly_buckets: list[list[float]] = [[] for _ in range(24)]

    for reading in heartrate_data:
        timestamp_str = reading.get("timestamp", "")
        bpm = reading.get("bpm")

        if timestamp_str and bpm is not None:
            try:
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                hour = dt.hour
                hourly_buckets[hour].append(bpm)
            except (ValueError, AttributeError):
                continue

    # Calculate average BPM for each hour
    hourly_data = []
    for hour in range(24):
        if hourly_buckets[hour]:
            avg_bpm = sum(hourly_buckets[hour]) / len(hourly_buckets[hour])
            hourly_data.append((hour, avg_bpm))

    if not hourly_data:
        return "No heart rate data"

    # Build Mermaid bar chart with dark theme
    lines = []
    lines.append("```mermaid")
    lines.append("%%{init: {'theme':'dark'}}%%")
    lines.append("xychart-beta")
    lines.append('    title "24-Hour Heart Rate"')
    lines.append('    x-axis "Hour" [' + ", ".join([f'"{h:02d}"' for h, _ in hourly_data]) + "]")
    lines.append('    y-axis "Average BPM" 40 --> 120')
    lines.append("    bar [" + ", ".join([f"{bpm:.0f}" for _, bpm in hourly_data]) + "]")
    lines.append("```")

    return "\n".join(lines)


def create_mermaid_bar_chart(met_items: list[float]) -> str:
    """
    Create a Mermaid bar chart from MET activity data.

    Args:
        met_items: List of MET values (one per minute, typically 1440 items for a day)

    Returns:
        Mermaid chart definition as string
    """
    # Group into hourly buckets (60 minutes per hour)
    hourly_buckets = []
    for hour in range(24):
        start_idx = hour * 60
        end_idx = start_idx + 60
        if start_idx < len(met_items):
            bucket = met_items[start_idx:end_idx]
            if bucket:
                avg_met = sum(bucket) / len(bucket)
                hourly_buckets.append((hour, avg_met))

    # Build Mermaid bar chart with dark theme
    lines = []
    lines.append("```mermaid")
    lines.append("%%{init: {'theme':'dark'}}%%")
    lines.append("xychart-beta")
    lines.append('    title "24-Hour MET Activity"')
    lines.append('    x-axis "Hour" [' + ", ".join([f'"{h:02d}"' for h, _ in hourly_buckets]) + "]")
    lines.append('    y-axis "Average MET" 0 --> 6')
    lines.append("    bar [" + ", ".join([f"{met:.2f}" for _, met in hourly_buckets]) + "]")
    lines.append("```")

    return "\n".join(lines)
