"""DataFrame formatting for Oura data."""

from typing import Any

import pandas as pd


def format_dataframe(data: Any) -> str:
    """
    Format data as pandas DataFrame.

    Args:
        data: Data to format (dict or list of dicts)

    Returns:
        DataFrame string representation
    """
    if isinstance(data, dict):
        # If dict contains lists, try to convert each list to a DataFrame
        if all(isinstance(v, list) for v in data.values()):
            result = []
            for key, values in data.items():
                if values:
                    result.append(f"\n{key}:\n{'-' * 40}")
                    df = pd.DataFrame(values)
                    result.append(df.to_string(index=False))
            return "\n".join(result) if result else "No data"
        # Single dict - convert to DataFrame
        df = pd.DataFrame([data])
        return str(df.to_string(index=False))
    if isinstance(data, list):
        if not data:
            return "No data"
        df = pd.DataFrame(data)
        return str(df.to_string(index=False))
    return str(data)
