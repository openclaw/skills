#!/usr/bin/env python3
"""
Backfill causal action log from email history.

Usage:
    # Using gog CLI
    gog gmail list --sent --after 2024-01-01 --format json > /tmp/sent.json
    python backfill_email.py /tmp/sent.json

    # Or let script query directly (requires gog configured)
    python backfill_email.py --days 90
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
    # Handle common formats
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
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


def infer_recipient_type(email_data):
    """Infer recipient type from email metadata."""
    # This is a heuristic - customize based on your patterns
    to_addr = email_data.get("to", "").lower()
    subject = email_data.get("subject", "").lower()
    
    if any(x in to_addr for x in ["reply", "re:", "follow"]):
        return "warm"
    if any(x in subject for x in ["intro", "reaching out", "connect"]):
        return "cold"
    return "existing"


def check_reply_exists(email_data, all_emails):
    """Check if a reply was received to this email."""
    # Simple heuristic: look for emails with Re: subject from recipient
    subject = email_data.get("subject", "")
    to_addr = email_data.get("to", "")
    sent_time = email_data.get("date", "")
    
    for other in all_emails:
        other_subject = other.get("subject", "")
        other_from = other.get("from", "")
        other_time = other.get("date", "")
        
        # Check if it's a reply
        if (f"Re: {subject}" in other_subject or 
            f"RE: {subject}" in other_subject):
            if to_addr and to_addr in other_from:
                if other_time > sent_time:
                    return True, other_time
    
    return False, None


def backfill_from_json(json_path, log_path, all_emails=None):
    """Backfill action log from JSON export."""
    with open(json_path) as f:
        emails = json.load(f)
    
    if all_emails is None:
        all_emails = emails
    
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for email in emails:
        sent_time = parse_time(email.get("date"))
        reply_received, reply_time = check_reply_exists(email, all_emails)
        
        event = {
            "action": "send_email",
            "domain": "email",
            "context": {
                "recipient_type": infer_recipient_type(email),
                "subject_length": len(email.get("subject", "")),
                "has_attachment": email.get("hasAttachment", False),
            },
            "time": sent_time,
            "pre_state": {
                "day_of_week": get_day_of_week(sent_time),
                "time_bucket": get_time_bucket(sent_time),
            },
            "post_state": {
                "reply_received": reply_received,
            },
            "outcome": "reply" if reply_received else "no_reply",
            "outcome_observed_at": reply_time or datetime.now(timezone.utc).isoformat(),
            "backfilled": True,
        }
        
        with open(path, "a") as f:
            f.write(json.dumps(event) + "\n")
        count += 1
    
    return count


def backfill_via_gog(days, log_path):
    """Backfill by querying gog directly."""
    after_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Get sent emails
    result = subprocess.run(
        ["gog", "gmail", "list", "--sent", "--after", after_date, "--format", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error running gog: {result.stderr}", file=sys.stderr)
        return 0
    
    sent_emails = json.loads(result.stdout) if result.stdout.strip() else []
    
    # Get all emails for reply checking
    result = subprocess.run(
        ["gog", "gmail", "list", "--after", after_date, "--format", "json"],
        capture_output=True, text=True
    )
    all_emails = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else sent_emails
    
    # Write to temp and process
    tmp_path = "/tmp/gog_sent_emails.json"
    with open(tmp_path, "w") as f:
        json.dump(sent_emails, f)
    
    return backfill_from_json(tmp_path, log_path, all_emails)


def main():
    parser = argparse.ArgumentParser(description="Backfill email actions")
    parser.add_argument("json_file", nargs="?", help="JSON file with email data")
    parser.add_argument("--days", "-d", type=int, default=90, help="Days to look back (if querying gog)")
    parser.add_argument("--log-path", "-l", default=DEFAULT_LOG_PATH, help="Action log path")
    
    args = parser.parse_args()
    
    if args.json_file:
        count = backfill_from_json(args.json_file, args.log_path)
    else:
        count = backfill_via_gog(args.days, args.log_path)
    
    print(f"Backfilled {count} email actions to {args.log_path}")


if __name__ == "__main__":
    main()
