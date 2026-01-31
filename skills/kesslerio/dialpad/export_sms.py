#!/usr/bin/env python3
"""
Export historical SMS via Dialpad Stats API.

Usage:
    python3 export_sms.py --output sms_export.csv
    python3 export_sms.py --start-date 2026-01-01 --end-date 2026-01-31 --output jan_sms.csv
    python3 export_sms.py --office-id 6194013244489728 --output office_sms.csv
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import time


# Configuration
DIALPAD_API_KEY = os.environ.get("DIALPAD_API_KEY")
DIALPAD_API_BASE = "https://dialpad.com/api/v2"


def export_sms(start_date=None, end_date=None, office_id=None, output=None):
    """
    Export SMS data via Dialpad Stats API.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        office_id: Optional office ID to filter
        output: Output file path (CSV)

    Returns:
        dict: Export job details with download URL
    """
    if not DIALPAD_API_KEY:
        raise ValueError("DIALPAD_API_KEY environment variable not set")

    # Create export job
    url = f"{DIALPAD_API_BASE}/exports"

    payload = {
        "export_type": "records",
        "stat_type": "texts",
    }

    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date
    if office_id:
        payload["office_id"] = office_id

    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    request = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
            job = json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except:
            error_msg = error_body or str(e)
        raise RuntimeError(f"Dialpad API error (HTTP {e.code}): {error_msg}")

    # Poll for completion
    job_id = job.get("id")
    print(f"Export job created: {job_id}")
    print("Polling for completion...")

    status_url = f"{DIALPAD_API_BASE}/exports/{job_id}"
    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Accept": "application/json"
    }

    while True:
        request = urllib.request.Request(status_url, headers=headers, method="GET")
        
        try:
            with urllib.request.urlopen(request) as response:
                status_data = response.read().decode("utf-8")
                status = json.loads(status_data)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Status check failed: {e.code}")

        status_value = status.get("status")
        print(f"   Status: {status_value}")

        if status_value == "completed":
            download_url = status.get("url")
            print(f"   Download URL: {download_url}")
            
            if output:
                # Download the file
                print(f"   Downloading to {output}...")
                download_request = urllib.request.Request(download_url)
                with urllib.request.urlopen(download_request) as response:
                    content = response.read()
                    with open(output, "wb") as f:
                        f.write(content)
                print(f"   Saved to {output}")
            
            return status

        elif status_value == "failed":
            raise RuntimeError(f"Export failed: {status.get('error')}")

        elif status_value in ["pending", "running"]:
            time.sleep(5)
            continue

        else:
            raise RuntimeError(f"Unknown status: {status_value}")


def main():
    parser = argparse.ArgumentParser(
        description="Export historical SMS via Dialpad Stats API"
    )
    parser.add_argument(
        "--start-date",
        dest="start_date",
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        dest="end_date",
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--office-id",
        dest="office_id",
        help="Office ID to filter (optional)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path for CSV"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    try:
        result = export_sms(
            start_date=args.start_date,
            end_date=args.end_date,
            office_id=args.office_id,
            output=args.output
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Export completed!")
            if args.output:
                print(f"   File: {args.output}")
            print(f"   Status: {result.get('status')}")

        sys.exit(0)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
