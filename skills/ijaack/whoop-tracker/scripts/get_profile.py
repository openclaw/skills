#!/usr/bin/env python3
"""
Get WHOOP user profile and body measurements.

Example:
    python3 get_profile.py
    python3 get_profile.py --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whoop_client import WhoopClient


def main():
    parser = argparse.ArgumentParser(description="Get WHOOP user profile")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    try:
        client = WhoopClient()
        profile = client.get_profile()
        body = client.get_body_measurements()
    except FileNotFoundError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"profile": profile, "body_measurements": body}, indent=2))
        return

    height_m = body.get("height_meter", 0)
    weight_kg = body.get("weight_kilogram", 0)

    print("\nWHOOP User Profile\n")
    print("-" * 50)
    print(f"  Name:     {profile.get('first_name')} {profile.get('last_name')}")
    print(f"  Email:    {profile.get('email')}")
    print(f"  User ID:  {profile.get('user_id')}")
    print()
    print("Body Measurements:")
    print(f"  Height:   {height_m} m  ({round(height_m * 100, 1)} cm)")
    print(f"  Weight:   {weight_kg} kg ({round(weight_kg * 2.20462, 1)} lbs)")
    print(f"  Max HR:   {body.get('max_heart_rate')} bpm")
    print()


if __name__ == "__main__":
    main()
