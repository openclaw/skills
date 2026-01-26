"""Shared utilities for chart generation."""

from datetime import datetime


def bucket_timeseries_data(
    data: list[dict],
    timestamp_key: str,
    value_key: str,
    bucket_minutes: int,
    buckets_per_day: int,
) -> list[float | None]:
    """Bucket irregular time-series data into fixed-interval buckets.

    Args:
        data: List of dicts with timestamp and value keys
        timestamp_key: Key for timestamp field in data
        value_key: Key for value field in data
        bucket_minutes: Minutes per bucket
        buckets_per_day: Total buckets in a 24-hour period

    Returns:
        List of averaged values per bucket (None for missing data)
    """
    buckets: list[list[float]] = [[] for _ in range(buckets_per_day)]

    for reading in data:
        timestamp_str = reading.get(timestamp_key, "")
        value = reading.get(value_key)

        if timestamp_str and value is not None:
            try:
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                total_minutes = dt.hour * 60 + dt.minute
                bucket_idx = total_minutes // bucket_minutes
                if 0 <= bucket_idx < buckets_per_day:
                    buckets[bucket_idx].append(float(value))
            except (ValueError, AttributeError):
                continue

    # Calculate averages
    return [sum(bucket) / len(bucket) if bucket else None for bucket in buckets]


def bucket_regular_data(
    data: list[float],
    target_buckets: int,
    aggregation: str = "max",
) -> list[float]:
    """Bucket regular data (e.g., minute-by-minute) into larger buckets.

    Args:
        data: List of values (e.g., 1440 items for minute resolution)
        target_buckets: Number of buckets to create
        aggregation: Aggregation method ('max' or 'avg')

    Returns:
        List of aggregated values per bucket
    """
    if not data:
        return []

    bucket_size = len(data) // target_buckets
    if bucket_size == 0:
        bucket_size = 1

    buckets = []
    for i in range(0, len(data), bucket_size):
        bucket = data[i : i + bucket_size]
        if bucket:
            if aggregation == "max":
                buckets.append(max(bucket))
            else:  # avg
                buckets.append(sum(bucket) / len(bucket))

    return buckets[:target_buckets]


def create_hour_labels(num_buckets: int, buckets_per_hour: int) -> list[str]:
    """Create hour labels for chart x-axis.

    Args:
        num_buckets: Total number of buckets
        buckets_per_hour: Number of buckets per hour (e.g., 12 for 5-min resolution)

    Returns:
        List of labels (hour markers and empty strings)
    """
    labels = []
    for i in range(num_buckets):
        if i % buckets_per_hour == 0:
            hour = i // buckets_per_hour
            labels.append(f"{hour:02d}")
        else:
            labels.append("")
    return labels
