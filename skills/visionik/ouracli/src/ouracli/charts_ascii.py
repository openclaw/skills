"""ASCII/Braille chart generation for terminal output."""

from ouracli.chart_utils import bucket_regular_data, bucket_timeseries_data


def create_heartrate_bar_chart_ascii(
    heartrate_data: list[dict], width: int = 72, height: int = 10
) -> str:
    """
    Create an ASCII bar chart from heart rate data using Braille characters.

    Args:
        heartrate_data: List of dicts with 'timestamp' and 'bpm' keys
        width: Width of chart in characters (default 72 = 144 buckets)
        height: Height of chart in characters (default 10)

    Returns:
        ASCII bar chart as string
    """
    if not heartrate_data:
        return "No heart rate data"

    # Get actual min/max from raw data for Y-axis labels
    all_bpms: list[float] = [
        float(reading.get("bpm"))  # type: ignore[arg-type]
        for reading in heartrate_data
        if reading.get("bpm") is not None
    ]
    actual_min: float = (min(all_bpms) - 10) if all_bpms else 0.0
    actual_max: float = max(all_bpms) if all_bpms else 100.0

    # Create 144 buckets (24 hours * 6 = one bucket per 10 minutes)
    bucket_averages = bucket_timeseries_data(
        heartrate_data, "timestamp", "bpm", bucket_minutes=10, buckets_per_day=144
    )

    # Replace None with 0 for ASCII chart
    buckets = [v if v is not None else 0 for v in bucket_averages]

    return _create_ascii_bar_chart_from_buckets(
        buckets, width, height, "BPM", actual_min, actual_max
    )


def create_ascii_bar_chart(met_items: list[float], width: int = 72, height: int = 10) -> str:
    """
    Create an ASCII bar chart from MET data using Braille characters for higher resolution.

    Args:
        met_items: List of MET values (typically 1440 items for a full day)
        width: Width of chart in characters (default 72 = 144 buckets = 10 min/bucket)
        height: Height of chart in characters (default 10)

    Returns:
        ASCII bar chart as string
    """
    if not met_items:
        return "No MET data"

    # Group items into buckets - use 2x width since we'll pack 2 bars per character
    # 1440 items -> 144 buckets = 10 items per bucket (10 minutes each)
    num_buckets = width * 2
    buckets = bucket_regular_data(met_items, target_buckets=num_buckets, aggregation="max")

    return _create_ascii_bar_chart_from_buckets(buckets, width, height, "MET")


def _create_ascii_bar_chart_from_buckets(
    buckets: list[float],
    width: int,
    height: int,
    unit: str,
    actual_min: float | None = None,
    actual_max: float | None = None,
) -> str:
    """
    Internal function to create ASCII bar chart from pre-bucketed data.

    Args:
        buckets: List of values (should be width * 2 for dual-column packing)
        width: Width in characters
        height: Height in characters
        unit: Unit label (e.g., "MET" or "BPM")
        actual_min: Actual minimum value from source data (for Y-axis labels)
        actual_max: Actual maximum value from source data (for Y-axis labels)

    Returns:
        ASCII bar chart as string
    """
    # Braille patterns for vertical bars
    # Dots are arranged: 1,2,3,7 (left column), 4,5,6,8 (right column)
    #   1 • • 4
    #   2 • • 5
    #   3 • • 6
    #   7 • • 8
    # Bit positions: 0=1, 1=2, 2=3, 3=4, 4=5, 5=6, 6=7, 7=8
    braille_base = 0x2800

    # Left column patterns (dots 1,2,3,7) from bottom to top
    left_patterns = [
        0b00000000,  # 0: no dots
        0b01000000,  # 1: dot 7 (bit 6)
        0b01000100,  # 2: dots 3,7 (bits 2,6)
        0b01000110,  # 3: dots 2,3,7 (bits 1,2,6)
        0b01000111,  # 4: dots 1,2,3,7 (bits 0,1,2,6)
    ]

    # Right column patterns (dots 4,5,6,8) from bottom to top
    right_patterns = [
        0b00000000,  # 0: no dots
        0b10000000,  # 1: dot 8 (bit 7)
        0b10100000,  # 2: dots 6,8 (bits 5,7)
        0b10110000,  # 3: dots 5,6,8 (bits 4,5,7)
        0b10111000,  # 4: dots 4,5,6,8 (bits 3,4,5,7)
    ]

    # Find max value for scaling (use actual if provided, otherwise bucketed)
    max_val = actual_max if actual_max is not None else (max(buckets) if buckets else 1.0)
    if max_val == 0:
        max_val = 1.0

    # Find min value (use actual if provided, otherwise from non-zero buckets)
    if actual_min is not None:
        min_val = actual_min
    else:
        non_zero_vals = [v for v in buckets if v > 0]
        min_val = min(non_zero_vals) if non_zero_vals else 0

    # Each character has 4 dots of resolution, so total resolution is height * 4
    total_dots = height * 4

    # Calculate Y-axis labels (show 5 evenly distributed labels)
    y_labels = {}
    num_labels = min(5, height)  # Show up to 5 labels

    for i in range(num_labels):
        # Distribute labels evenly from top (max) to bottom (min)
        row = int(i * (height - 1) / (num_labels - 1))
        # Calculate value at this row linearly from max to min
        fraction = i / (num_labels - 1)
        value_at_row = max_val - fraction * (max_val - min_val)
        # Round to appropriate precision based on value range
        if max_val - min_val > 20:
            y_labels[row] = f"{value_at_row:.0f}"  # Integer for large ranges
        else:
            y_labels[row] = f"{value_at_row:.1f}"  # One decimal for small ranges

    # Find max label width for alignment
    max_label_width = max(len(label) for label in y_labels.values()) if y_labels else 0

    # Create chart lines from top to bottom
    lines = []
    for row in range(height):
        # Add Y-axis label if this row has one
        if row in y_labels:
            label = y_labels[row].rjust(max_label_width)
            line = f"{label} │ "
        else:
            line = " " * max_label_width + " │ "

        # Process buckets in pairs (left and right columns)
        for i in range(0, len(buckets), 2):
            left_val = buckets[i] if i < len(buckets) else 0
            right_val = buckets[i + 1] if i + 1 < len(buckets) else 0

            # Calculate dots for left bar (scale from min to max)
            value_range = max_val - min_val
            if value_range > 0 and left_val > 0:
                left_dots_filled = int(((left_val - min_val) / value_range) * total_dots)
            else:
                left_dots_filled = 0

            row_bottom = total_dots - (row + 1) * 4
            row_top = row_bottom + 4

            if left_dots_filled <= row_bottom:
                left_pattern = left_patterns[0]
            elif left_dots_filled >= row_top:
                left_pattern = left_patterns[4]
            else:
                dots_in_row = left_dots_filled - row_bottom
                left_pattern = left_patterns[dots_in_row]

            # Calculate dots for right bar (scale from min to max)
            if value_range > 0 and right_val > 0:
                right_dots_filled = int(((right_val - min_val) / value_range) * total_dots)
            else:
                right_dots_filled = 0

            if right_dots_filled <= row_bottom:
                right_pattern = right_patterns[0]
            elif right_dots_filled >= row_top:
                right_pattern = right_patterns[4]
            else:
                dots_in_row = right_dots_filled - row_bottom
                right_pattern = right_patterns[dots_in_row]

            # Combine left and right patterns
            combined_pattern = left_pattern | right_pattern
            char = chr(braille_base + combined_pattern)
            line += char
        lines.append(line)

    # Add a baseline with Y-axis alignment
    baseline = " " * max_label_width + " └" + "─" * width
    lines.append(baseline)

    # Add hour labels (0-23) with Y-axis alignment
    # Each hour = 6 buckets (60 min / 10 min per bucket)
    # With 2 buckets per character = 3 characters per hour
    # Build hour labels with proper spacing (each hour gets 3 chars)
    hour_parts = []
    for hour in range(24):
        if hour < 10:
            # Single digit: " X " (space, digit, space)
            hour_parts.append(f" {hour} ")
        else:
            # Double digit: "XX " (digit, digit, space)
            hour_parts.append(f"{hour} ")

    # Trim to exactly 72 characters and add Y-axis padding
    hour_line = " " * (max_label_width + 3) + "".join(hour_parts)[:width]
    lines.append(hour_line)

    return "\n".join(lines)
