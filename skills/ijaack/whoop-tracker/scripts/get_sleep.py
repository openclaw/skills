#!/usr/bin/env python3
"""
Get WHOOP sleep data.

Examples:
    python3 get_sleep.py --last
    python3 get_sleep.py --days 7
    python3 get_sleep.py --start 2026-01-20 --end 2026-01-27
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whoop_client import WhoopClient


def ms_to_hm(ms):
    """Convert milliseconds to h:mm string."""
    if not ms:
        return "0:00"
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    return f"{hours}:{minutes:02d}"


def format_sleep(record):
    """Format sleep record for display."""
    score = record.get("score") or {}
    stages = score.get("stage_summary") or {}
    needed = score.get("sleep_needed") or {}

    total_sleep_ms = (
        stages.get("total_light_sleep_time_milli", 0)
        + stages.get("total_slow_wave_sleep_time_milli", 0)
        + stages.get("total_rem_sleep_time_milli", 0)
    )

    return {
        "date": record.get("start", "")[:10],
        "is_nap": record.get("nap", False),
        "score_state": record.get("score_state", "UNKNOWN"),
        "total_sleep": ms_to_hm(total_sleep_ms),
        "in_bed": ms_to_hm(stages.get("total_in_bed_time_milli")),
        "rem": ms_to_hm(stages.get("total_rem_sleep_time_milli")),
        "deep": ms_to_hm(stages.get("total_slow_wave_sleep_time_milli")),
        "light": ms_to_hm(stages.get("total_light_sleep_time_milli")),
        "awake": ms_to_hm(stages.get("total_awake_time_milli")),
        "performance": score.get("sleep_performance_percentage"),
        "efficiency": round(score.get("sleep_efficiency_percentage", 0), 1) if score.get("sleep_efficiency_percentage") else None,
        "consistency": score.get("sleep_consistency_percentage"),
        "respiratory_rate": round(score.get("respiratory_rate", 0), 1) if score.get("respiratory_rate") else None,
        "disturbances": stages.get("disturbance_count"),
        "cycles": stages.get("sleep_cycle_count"),
        "sleep_needed": ms_to_hm(needed.get("baseline_milli")),
        "debt": ms_to_hm(needed.get("need_from_sleep_debt_milli")),
    }


def main():
    parser = argparse.ArgumentParser(description="Get WHOOP sleep data")
    parser.add_argument("--last", action="store_true", help="Get last night's sleep")
    parser.add_argument("--days", type=int, help="Get sleep for past N days")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--limit", type=int, default=25, help="Max records (default 25, max 25)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    start = None
    end = None

    if args.last:
        start = (now - timedelta(hours=48)).isoformat()
        end = now.isoformat()
        args.limit = 1
    elif args.days:
        start = (now - timedelta(days=args.days)).isoformat()
        end = now.isoformat()
    else:
        start = args.start
        end = args.end

    try:
        client = WhoopClient()
        response = client.get_sleep_collection(start=start, end=end, limit=args.limit)
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
        print("No sleep data found for the specified period.")
        return

    print(f"\nSleep Data ({len(records)} records)\n")
    print("-" * 70)

    for record in records:
        f = format_sleep(record)
        nap_tag = " (NAP)" if f["is_nap"] else ""
        if f["score_state"] != "SCORED":
            print(f"Date: {f['date']}{nap_tag}  [{f['score_state']}]")
            print()
            continue
        print(f"Date: {f['date']}{nap_tag}")
        print(f"  Total Sleep:   {f['total_sleep']}  (In bed: {f['in_bed']})")
        print(f"    REM: {f['rem']}  |  Deep: {f['deep']}  |  Light: {f['light']}  |  Awake: {f['awake']}")
        print(f"  Performance:   {f['performance']}%")
        if f["efficiency"]:
            print(f"  Efficiency:    {f['efficiency']}%  |  Consistency: {f['consistency']}%")
        if f["respiratory_rate"]:
            print(f"  Resp. Rate:    {f['respiratory_rate']} bpm")
        print(f"  Disturbances:  {f['disturbances']}  |  Sleep Cycles: {f['cycles']}")
        print(f"  Sleep Needed:  {f['sleep_needed']}  |  Debt: {f['debt']}")
        print()


if __name__ == "__main__":
    main()
