#!/usr/bin/env python3
"""
Backfill causal action log from calendar history.

Usage:
    # Using gog CLI
    gog calendar list --after 2024-01-01 --format json > /tmp/events.json
    python backfill_calendar.py /tmp/events.json

    # Or query directly
    python backfill_calendar.py --days 90
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DEFAULT_LOG_PATH = "memory/causal/action_log.jsonl"


def parse_time(time_str):
    """Parse various time formats to ISO."""
    if not time_str:
        return None
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]:
        try:
            return datetime.strptime(time_str, fmt).isoformat()
        except ValueError:
            continue
    return time_str


def get_time_bucket(iso_time):
    """Categorize time into morning/afternoon/evening."""
    if not iso_time:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        else:
            return "evening"
    except:
        return "unknown"


def get_day_of_week(iso_time):
    """Get day of week from ISO time."""
    if not iso_time:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        return dt.strftime("%A").lower()
    except:
        return "unknown"


def infer_meeting_outcome(event):
    """Infer if meeting happened, was cancelled, etc."""
    status = event.get("status", "").lower()
    
    if status == "cancelled":
        return "cancelled"
    
    # Check if event is in the past
    end_time = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_dt < datetime.now(timezone.utc):
                return "completed"
        except:
            pass
    
    return "scheduled"


def get_duration_minutes(event):
    """Calculate event duration in minutes."""
    start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
    end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
    
    if not start or not end:
        return None
    
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return int((end_dt - start_dt).total_seconds() / 60)
    except:
        return None


def backfill_from_json(json_path, log_path):
    """Backfill action log from JSON export."""
    with open(json_path) as f:
        events = json.load(f)
    
    if isinstance(events, dict):
        events = events.get("items", events.get("events", []))
    
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for event in events:
        start_time = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        start_time = parse_time(start_time)
        
        attendees = event.get("attendees", [])
        attendee_count = len(attendees)
        
        # Determine action type
        creator = event.get("creator", {}).get("self", False)
        organizer = event.get("organizer", {}).get("self", False)
        
        if creator or organizer:
            action = "create_meeting"
        else:
            action = "accept_meeting"  # or invited
        
        outcome = infer_meeting_outcome(event)
        
        action_event = {
            "action": action,
            "domain": "calendar",
            "context": {
                "attendee_count": attendee_count,
                "duration_minutes": get_duration_minutes(event),
                "is_recurring": bool(event.get("recurringEventId")),
                "has_video": bool(event.get("hangoutLink") or event.get("conferenceData")),
            },
            "time": event.get("created") or start_time,
            "pre_state": {
                "scheduled_time": start_time,
                "day_of_week": get_day_of_week(start_time),
                "time_bucket": get_time_bucket(start_time),
            },
            "post_state": {
                "status": outcome,
            },
            "outcome": outcome,
            "outcome_observed_at": datetime.now(timezone.utc).isoformat(),
            "backfilled": True,
        }
        
        with open(path, "a") as f:
            f.write(json.dumps(action_event) + "\n")
        count += 1
    
    return count


def backfill_via_gog(days, log_path):
    """Backfill by querying gog directly."""
    after_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    result = subprocess.run(
        ["gog", "calendar", "list", "--after", after_date, "--format", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error running gog: {result.stderr}", file=sys.stderr)
        return 0
    
    tmp_path = "/tmp/gog_calendar.json"
    with open(tmp_path, "w") as f:
        f.write(result.stdout)
    
    return backfill_from_json(tmp_path, log_path)


def main():
    parser = argparse.ArgumentParser(description="Backfill calendar actions")
    parser.add_argument("json_file", nargs="?", help="JSON file with calendar data")
    parser.add_argument("--days", "-d", type=int, default=90, help="Days to look back")
    parser.add_argument("--log-path", "-l", default=DEFAULT_LOG_PATH, help="Action log path")
    
    args = parser.parse_args()
    
    if args.json_file:
        count = backfill_from_json(args.json_file, args.log_path)
    else:
        count = backfill_via_gog(args.days, args.log_path)
    
    print(f"Backfilled {count} calendar actions to {args.log_path}")


if __name__ == "__main__":
    main()
