"""Chart.js configuration generation for HTML output."""

import json

from ouracli.chart_utils import bucket_regular_data, bucket_timeseries_data, create_hour_labels


def create_chartjs_heartrate_config(heartrate_data: list[dict], chart_id: str) -> str:
    """
    Create Chart.js configuration for heart rate data.

    Args:
        heartrate_data: List of dicts with 'timestamp' and 'bpm' keys
        chart_id: Unique ID for the chart

    Returns:
        JavaScript code to render the chart
    """
    if not heartrate_data:
        return ""

    # Get actual min/max from raw data for Y-axis range
    all_bpms: list[float] = [
        float(reading.get("bpm"))  # type: ignore[arg-type]
        for reading in heartrate_data
        if reading.get("bpm") is not None
    ]
    if not all_bpms:
        return ""

    actual_min: float = min(all_bpms) - 10  # Floor 10 BPM below minimum
    actual_max: float = max(all_bpms)

    # Create 288 buckets (24 hours * 12 = one bucket per 5 minutes)
    bucket_averages = bucket_timeseries_data(
        heartrate_data, "timestamp", "bpm", bucket_minutes=5, buckets_per_day=288
    )

    # Create labels: show hour labels at hour boundaries
    labels = create_hour_labels(num_buckets=288, buckets_per_hour=12)

    # Convert None to null and keep numbers as-is for Chart.js
    data_values = [round(v) if v is not None else None for v in bucket_averages]

    return f"""
    new Chart(document.getElementById('{chart_id}'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(labels)},
            datasets: [{{
                label: 'BPM (5-min avg)',
                data: {json.dumps(data_values)},
                backgroundColor: 'rgba(76, 175, 80, 0.8)',
                borderColor: 'rgba(46, 125, 50, 1)',
                borderWidth: 0,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    display: false
                }},
                title: {{
                    display: true,
                    text: '24-Hour Heart Rate (5-minute resolution)',
                    color: '#333',
                    font: {{
                        size: 16
                    }}
                }},
                tooltip: {{
                    callbacks: {{
                        title: function(context) {{
                            const idx = context[0].dataIndex;
                            const hour = Math.floor(idx / 12);
                            const minute = (idx % 12) * 5;
                            const hourStr = hour.toString().padStart(2, '0');
                            const minStr = minute.toString().padStart(2, '0');
                            return hourStr + ':' + minStr;
                        }}
                    }}
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: false,
                    min: {actual_min},
                    max: {actual_max},
                    title: {{
                        display: true,
                        text: 'BPM',
                        color: '#666'
                    }},
                    ticks: {{
                        color: '#666'
                    }},
                    grid: {{
                        color: 'rgba(0, 0, 0, 0.1)'
                    }}
                }},
                x: {{
                    title: {{
                        display: true,
                        text: 'Hour',
                        color: '#666'
                    }},
                    ticks: {{
                        color: '#666',
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    }},
                    grid: {{
                        color: function(context) {{
                            // Hour boundaries have darker grid lines
                            const isHourBoundary = context.index % 12 === 0;
                            return isHourBoundary ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.05)';
                        }}
                    }}
                }}
            }}
        }}
    }});
    """


def create_chartjs_config(met_items: list[float], chart_id: str) -> str:
    """
    Create Chart.js configuration for MET activity data.

    Args:
        met_items: List of MET values (one per minute, typically 1440 items)
        chart_id: Unique ID for the chart

    Returns:
        JavaScript code to render the chart
    """
    # Group into 5-minute buckets (288 buckets = 24 hours * 12)
    five_minute_buckets = bucket_regular_data(met_items, target_buckets=288, aggregation="avg")

    # Pad with zeros if needed
    while len(five_minute_buckets) < 288:
        five_minute_buckets.append(0)

    # Create labels: show hour labels at hour boundaries
    labels = create_hour_labels(num_buckets=288, buckets_per_hour=12)

    # Round to 2 decimal places for MET values
    data_values = [round(v, 2) for v in five_minute_buckets]

    return f"""
    new Chart(document.getElementById('{chart_id}'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(labels)},
            datasets: [{{
                label: 'MET (5-min avg)',
                data: {json.dumps(data_values)},
                backgroundColor: 'rgba(76, 175, 80, 0.8)',
                borderColor: 'rgba(46, 125, 50, 1)',
                borderWidth: 0,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    display: false
                }},
                title: {{
                    display: true,
                    text: '24-Hour MET Activity (5-minute resolution)',
                    color: '#333',
                    font: {{
                        size: 16
                    }}
                }},
                tooltip: {{
                    callbacks: {{
                        title: function(context) {{
                            const idx = context[0].dataIndex;
                            const hour = Math.floor(idx / 12);
                            const minute = (idx % 12) * 5;
                            const hourStr = hour.toString().padStart(2, '0');
                            const minStr = minute.toString().padStart(2, '0');
                            return hourStr + ':' + minStr;
                        }}
                    }}
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    max: 6,
                    title: {{
                        display: true,
                        text: 'MET',
                        color: '#666'
                    }},
                    ticks: {{
                        color: '#666'
                    }},
                    grid: {{
                        color: 'rgba(0, 0, 0, 0.1)'
                    }}
                }},
                x: {{
                    title: {{
                        display: true,
                        text: 'Hour',
                        color: '#666'
                    }},
                    ticks: {{
                        color: '#666',
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    }},
                    grid: {{
                        color: function(context) {{
                            // Hour boundaries have darker grid lines
                            const isHourBoundary = context.index % 12 === 0;
                            return isHourBoundary ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.05)';
                        }}
                    }}
                }}
            }}
        }}
    }});
    """
