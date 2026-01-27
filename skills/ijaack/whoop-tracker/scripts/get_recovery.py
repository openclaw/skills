#!/usr/bin/env python3
"""
Get WHOOP recovery data.

Examples:
    python3 get_recovery.py --today
    python3 get_recovery.py --days 7
    python3 get_recovery.py --start 2026-01-20 --end 2026-01-27
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whoop_client import WhoopClient


def format_recovery(record):
    """Format recovery record for display."""
    score = record.get("score") or {}
    return {
        "date": record.get("created_at", "")[:10],
        "recovery_score": score.get("recovery_score"),
        "hrv_rmssd": round(score.get("hrv_rmssd_milli", 0), 1),
        "resting_hr": score.get("resting_heart_rate"),
        "spo2": round(score.get("spo2_percentage", 0), 1) if score.get("spo2_percentage") else None,
        "skin_temp": round(score.get("skin_temp_celsius", 0), 1) if score.get("skin_temp_celsius") else None,
        "calibrating": score.get("user_calibrating", False),
        "score_state": record.get("score_state", "UNKNOWN"),
    }


def main():
    parser = argparse.ArgumentParser(description="Get WHOOP recovery data")
    parser.add_argument("--today", action="store_true", help="Get today's recovery")
    parser.add_argument("--days", type=int, help="Get recovery for past N days")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--limit", type=int, default=25, help="Max records (default 25, max 25)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    start = None
    end = None

    if args.today:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end = now.isoformat()
    elif args.days:
        start = (now - timedelta(days=args.days)).isoformat()
        end = now.isoformat()
    else:
        start = args.start
        end = args.end

    try:
        client = WhoopClient()
        response = client.get_recovery_collection(start=start, end=end, limit=args.limit)
    except FileNotFoundError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(response, indent=2))
        return

    records = response.get("records", [])
    if not records:
        print("No recovery data found for the specified period.")
        return

    print(f"\nRecovery Data ({len(records)} records)\n")
    print("-" * 70)

    for record in records:
        f = format_recovery(record)
        if f["score_state"] != "SCORED":
            print(f"Date: {f['date']}  [{f['score_state']}]")
            print()
            continue
        print(f"Date: {f['date']}")
        print(f"  Recovery Score: {f['recovery_score']}%")
        print(f"  HRV (RMSSD):   {f['hrv_rmssd']} ms")
        print(f"  Resting HR:    {f['resting_hr']} bpm")
        if f["spo2"]:
            print(f"  SpO2:          {f['spo2']}%")
        if f["skin_temp"]:
            print(f"  Skin Temp:     {f['skin_temp']}°C")
        if f["calibrating"]:
            print("  ⚠️  User is calibrating")
        print()


if __name__ == "__main__":
    main()
