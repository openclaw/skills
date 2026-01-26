#!/usr/bin/env python3
"""
Backfill causal action log from message history (WhatsApp, Discord, Slack).

Usage:
    # WhatsApp via wacli
    wacli search --after 2024-01-01 --from me --format json > /tmp/wa_sent.json
    python backfill_messages.py /tmp/wa_sent.json --platform whatsapp

    # Or query directly
    python backfill_messages.py --platform whatsapp --days 90
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

DEFAULT_LOG_PATH = "memory/causal/action_log.jsonl"


def parse_time(time_str):
    """Parse various time formats to ISO."""
    if not time_str:
        return None
    if isinstance(time_str, (int, float)):
        return datetime.fromtimestamp(time_str, tz=timezone.utc).isoformat()
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


def find_response(msg, all_messages, max_hours=48):
    """Find if there was a response to this message."""
    chat_id = msg.get("chat_id") or msg.get("chatId") or msg.get("channel_id")
    sent_time = parse_time(msg.get("timestamp") or msg.get("date") or msg.get("time"))
    
    if not chat_id or not sent_time:
        return False, None, None
    
    sent_dt = datetime.fromisoformat(sent_time.replace("Z", "+00:00"))
    max_response_time = sent_dt + timedelta(hours=max_hours)
    
    for other in all_messages:
        other_chat = other.get("chat_id") or other.get("chatId") or other.get("channel_id")
        if other_chat != chat_id:
            continue
            
        # Skip if from me
        if other.get("from_me") or other.get("fromMe") or other.get("is_mine"):
            continue
        
        other_time = parse_time(other.get("timestamp") or other.get("date") or other.get("time"))
        if not other_time:
            continue
            
        other_dt = datetime.fromisoformat(other_time.replace("Z", "+00:00"))
        
        # Check if it's a response (after sent, within window)
        if sent_dt < other_dt <= max_response_time:
            delay_hours = (other_dt - sent_dt).total_seconds() / 3600
            return True, other_time, delay_hours
    
    return False, None, None


def backfill_from_json(json_path, log_path, platform, all_messages=None):
    """Backfill action log from JSON export."""
    with open(json_path) as f:
        messages = json.load(f)
    
    if isinstance(messages, dict):
        messages = messages.get("messages", [])
    
    if all_messages is None:
        all_messages = messages
    
    # Filter to only sent messages
    sent_messages = [
        m for m in messages 
        if m.get("from_me") or m.get("fromMe") or m.get("is_mine")
    ]
    
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for msg in sent_messages:
        sent_time = parse_time(msg.get("timestamp") or msg.get("date") or msg.get("time"))
        response_received, response_time, delay_hours = find_response(msg, all_messages)
        
        message_text = msg.get("body") or msg.get("content") or msg.get("text") or ""
        
        event = {
            "action": "send_message",
            "domain": "messaging",
            "context": {
                "platform": platform,
                "message_length": len(message_text),
                "has_media": bool(msg.get("hasMedia") or msg.get("media")),
                "is_group": bool(msg.get("isGroup") or msg.get("is_group")),
            },
            "time": sent_time,
            "pre_state": {
                "time_bucket": get_time_bucket(sent_time),
            },
            "post_state": {
                "response_received": response_received,
                "response_delay_hours": delay_hours,
            },
            "outcome": "response" if response_received else "no_response",
            "outcome_observed_at": response_time or datetime.now(timezone.utc).isoformat(),
            "backfilled": True,
        }
        
        with open(path, "a") as f:
            f.write(json.dumps(event) + "\n")
        count += 1
    
    return count


def backfill_whatsapp(days, log_path):
    """Backfill from WhatsApp via wacli."""
    after_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    result = subprocess.run(
        ["wacli", "search", "--after", after_date, "--limit", "1000", "--format", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error running wacli: {result.stderr}", file=sys.stderr)
        return 0
    
    all_messages = json.loads(result.stdout) if result.stdout.strip() else []
    
    tmp_path = "/tmp/wacli_messages.json"
    with open(tmp_path, "w") as f:
        json.dump(all_messages, f)
    
    return backfill_from_json(tmp_path, log_path, "whatsapp", all_messages)


def main():
    parser = argparse.ArgumentParser(description="Backfill message actions")
    parser.add_argument("json_file", nargs="?", help="JSON file with message data")
    parser.add_argument("--platform", "-p", default="whatsapp", 
                       choices=["whatsapp", "discord", "slack", "telegram"],
                       help="Messaging platform")
    parser.add_argument("--days", "-d", type=int, default=90, help="Days to look back")
    parser.add_argument("--log-path", "-l", default=DEFAULT_LOG_PATH, help="Action log path")
    
    args = parser.parse_args()
    
    if args.json_file:
        count = backfill_from_json(args.json_file, args.log_path, args.platform)
    elif args.platform == "whatsapp":
        count = backfill_whatsapp(args.days, args.log_path)
    else:
        print(f"Direct query not implemented for {args.platform}. Provide JSON file.", 
              file=sys.stderr)
        return
    
    print(f"Backfilled {count} message actions to {args.log_path}")


if __name__ == "__main__":
    main()
