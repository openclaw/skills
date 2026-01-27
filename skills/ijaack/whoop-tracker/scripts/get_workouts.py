#!/usr/bin/env python3
"""
Get WHOOP workout data.

Examples:
    python3 get_workouts.py --days 7
    python3 get_workouts.py --sport running
    python3 get_workouts.py --start 2026-01-20 --end 2026-01-27
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whoop_client import WhoopClient


def ms_to_min(ms):
    """Convert milliseconds to minutes."""
    return round(ms / 60000, 1) if ms else 0


def pretty_sport_name(raw: str) -> str:
    """Convert WHOOP sport name to human-friendly label."""
    if not raw:
        return "Unknown"
    s = raw.lower()

    # Common WHOOP sport codes
    mappings = {
        "weightlifting_msk": "Strength training (weightlifting)",
        "weightlifting": "Strength training",
        "strength_training": "Strength training",
        "functional_fitness": "Functional fitness",
        "running": "Running",
        "cycling": "Cycling",
        "swimming": "Swimming",
        "walking": "Walking",
        "yoga": "Yoga",
        "pilates": "Pilates",
        "basketball": "Basketball",
        "soccer": "Soccer",
        "tennis": "Tennis",
        "hiking": "Hiking",
        "skiing": "Skiing",
        "snowboarding": "Snowboarding",
        "rowing": "Rowing",
        "crossfit": "CrossFit",
        "boxing": "Boxing",
        "climbing": "Climbing",
        "dance": "Dance",
        "hiit": "HIIT",
    }

    if s in mappings:
        return mappings[s]

    # Default: replace underscores and title-case
    return s.replace("_", " ").title()


def format_workout(record):
    """Format workout record for display."""
    score = record.get("score") or {}
    zones = score.get("zone_durations") or {}

    total_ms = sum(zones.get(f"zone_{z}_milli", 0) for z in ["zero", "one", "two", "three", "four", "five"])

    return {
        "date": record.get("start", "")[:10],
        "sport": pretty_sport_name(record.get("sport_name", "Unknown")),
        "score_state": record.get("score_state", "UNKNOWN"),
        "strain": round(score.get("strain", 0), 1),
        "duration_min": ms_to_min(total_ms),
        "avg_hr": score.get("average_heart_rate"),
        "max_hr": score.get("max_heart_rate"),
        "calories_kcal": round(score.get("kilojoule", 0) * 0.239006) if score.get("kilojoule") else None,
        "distance_km": round(score.get("distance_meter", 0) / 1000, 2) if score.get("distance_meter") else None,
        "altitude_gain_m": round(score.get("altitude_gain_meter", 0)) if score.get("altitude_gain_meter") else None,
        "percent_recorded": score.get("percent_recorded"),
        "zones": {
            f"Z{i}": ms_to_min(zones.get(k))
            for i, k in enumerate(
                ["zone_zero_milli", "zone_one_milli", "zone_two_milli",
                 "zone_three_milli", "zone_four_milli", "zone_five_milli"]
            )
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Get WHOOP workout data")
    parser.add_argument("--days", type=int, help="Get workouts for past N days")
    parser.add_argument("--sport", help="Filter by sport name (case-insensitive)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--limit", type=int, default=25, help="Max records (default 25, max 25)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    start = None
    end = None

    if args.days:
        start = (now - timedelta(days=args.days)).isoformat()
        end = now.isoformat()
    else:
        start = args.start
        end = args.end

    try:
        client = WhoopClient()
        response = client.get_workout_collection(start=start, end=end, limit=args.limit)
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

    # Filter by sport if specified
    if args.sport:
        records = [r for r in records if r.get("sport_name", "").lower() == args.sport.lower()]

    if not records:
        print("No workout data found for the specified period.")
        return

    print(f"\nWorkout Data ({len(records)} records)\n")
    print("-" * 70)

    for record in records:
        f = format_workout(record)
        if f["score_state"] != "SCORED":
            print(f"Date: {f['date']} | Sport: {f['sport']}  [{f['score_state']}]")
            print()
            continue
        print(f"Date: {f['date']} | Sport: {f['sport']}")
        print(f"  Strain:   {f['strain']}")
        print(f"  Duration: {f['duration_min']} min")
        print(f"  HR:       {f['avg_hr']} avg / {f['max_hr']} max bpm")
        if f["calories_kcal"]:
            print(f"  Calories: {f['calories_kcal']} kcal")
        if f["distance_km"]:
            print(f"  Distance: {f['distance_km']} km")
        if f["altitude_gain_m"]:
            print(f"  Elevation: +{f['altitude_gain_m']} m")
        if f["percent_recorded"] is not None:
            print(f"  Recorded: {f['percent_recorded']}%")

        zone_parts = [f"{k}: {v}m" for k, v in f["zones"].items() if v > 0]
        if zone_parts:
            print(f"  HR Zones: {' | '.join(zone_parts)}")
        print()


if __name__ == "__main__":
    main()
