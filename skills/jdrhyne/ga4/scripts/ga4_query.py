#!/usr/bin/env python3
"""
GA4 Data API Query Script

Query Google Analytics 4 properties for analytics data.
Requires: google-analytics-data, google-auth-oauthlib

Install: pip install google-analytics-data google-auth-oauthlib
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
        FilterExpression,
        Filter,
    )
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-analytics-data google-auth-oauthlib")
    sys.exit(1)


def get_credentials():
    """Get OAuth credentials from environment variables."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing environment variables.")
        print("Required: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN")
        sys.exit(1)
    
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )


def parse_filter(filter_str):
    """Parse filter string like 'pagePath=~/blog/' into FilterExpression."""
    if not filter_str:
        return None
    
    # Support patterns: dimension=value, dimension=~regex, dimension!=value
    if "=~" in filter_str:
        dim, pattern = filter_str.split("=~", 1)
        return FilterExpression(
            filter=Filter(
                field_name=dim.strip(),
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.PARTIAL_REGEXP,
                    value=pattern.strip(),
                ),
            )
        )
    elif "!=" in filter_str:
        dim, value = filter_str.split("!=", 1)
        return FilterExpression(
            filter=Filter(
                field_name=dim.strip(),
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.EXACT,
                    value=value.strip(),
                    case_sensitive=False,
                ),
            ),
            not_expression=True,
        )
    elif "=" in filter_str:
        dim, value = filter_str.split("=", 1)
        return FilterExpression(
            filter=Filter(
                field_name=dim.strip(),
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.CONTAINS,
                    value=value.strip(),
                    case_sensitive=False,
                ),
            )
        )
    return None


def run_report(property_id, metrics, dimensions, start_date, end_date, limit, filter_expr=None):
    """Run a GA4 report query."""
    credentials = get_credentials()
    client = BetaAnalyticsDataClient(credentials=credentials)
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )
    
    if filter_expr:
        request.dimension_filter = filter_expr
    
    return client.run_report(request)


def format_table(response, metrics, dimensions):
    """Format response as a table."""
    # Header
    headers = dimensions + metrics
    col_widths = [max(len(h), 10) for h in headers]
    
    # Calculate column widths from data
    rows = []
    for row in response.rows:
        values = [dv.value for dv in row.dimension_values] + [mv.value for mv in row.metric_values]
        rows.append(values)
        for i, v in enumerate(values):
            col_widths[i] = max(col_widths[i], len(str(v)[:50]))
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(v)[:50].ljust(col_widths[i]) for i, v in enumerate(row)))


def format_json(response, metrics, dimensions):
    """Format response as JSON."""
    results = []
    for row in response.rows:
        item = {}
        for i, dv in enumerate(row.dimension_values):
            item[dimensions[i]] = dv.value
        for i, mv in enumerate(row.metric_values):
            item[metrics[i]] = mv.value
        results.append(item)
    print(json.dumps(results, indent=2))


def format_csv(response, metrics, dimensions):
    """Format response as CSV."""
    headers = dimensions + metrics
    print(",".join(headers))
    for row in response.rows:
        values = [dv.value for dv in row.dimension_values] + [mv.value for mv in row.metric_values]
        # Escape commas in values
        escaped = [f'"{v}"' if "," in v else v for v in values]
        print(",".join(escaped))


def main():
    parser = argparse.ArgumentParser(description="Query GA4 Analytics Data API")
    parser.add_argument("--property", "-p", help="GA4 Property ID (or set GA4_PROPERTY_ID env var)")
    parser.add_argument("--metrics", "-m", default="screenPageViews", 
                        help="Comma-separated metrics (default: screenPageViews)")
    parser.add_argument("--metric", help="Single metric (alias for --metrics)")
    parser.add_argument("--dimensions", "-d", default="pagePath",
                        help="Comma-separated dimensions (default: pagePath)")
    parser.add_argument("--dimension", help="Single dimension (alias for --dimensions)")
    parser.add_argument("--start", "-s", help="Start date (YYYY-MM-DD, default: 30 days ago)")
    parser.add_argument("--end", "-e", help="End date (YYYY-MM-DD, default: today)")
    parser.add_argument("--limit", "-l", type=int, default=25, help="Max rows (default: 25)")
    parser.add_argument("--filter", "-f", help="Filter expression (e.g., 'pagePath=~/blog/')")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    
    args = parser.parse_args()
    
    # Get property ID
    property_id = args.property or os.environ.get("GA4_PROPERTY_ID")
    if not property_id:
        print("Error: GA4 Property ID required. Use --property or set GA4_PROPERTY_ID env var.")
        print("\nFind your Property ID in GA4:")
        print("  Admin → Property Settings → Property ID (numeric)")
        sys.exit(1)
    
    # Parse metrics and dimensions
    metrics = (args.metric or args.metrics).split(",")
    dimensions = (args.dimension or args.dimensions).split(",")
    
    # Parse dates (default: last 30 days)
    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    start_date = args.start or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Parse filter
    filter_expr = parse_filter(args.filter)
    
    try:
        response = run_report(
            property_id=property_id,
            metrics=metrics,
            dimensions=dimensions,
            start_date=start_date,
            end_date=end_date,
            limit=args.limit,
            filter_expr=filter_expr,
        )
        
        if args.json:
            format_json(response, metrics, dimensions)
        elif args.csv:
            format_csv(response, metrics, dimensions)
        else:
            print(f"\nGA4 Report: {start_date} to {end_date}")
            print(f"Property: {property_id}\n")
            format_table(response, metrics, dimensions)
            print(f"\nTotal rows: {response.row_count}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
