#!/usr/bin/env python3
"""
Proactive Research Monitor

Checks topics due for monitoring, scores findings, and sends alerts.
Run via cron for automated monitoring.
"""

import sys
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    load_config, load_state, save_state, get_settings,
    get_channel_config, save_finding
)
from importance_scorer import score_result


def hash_url(url: str) -> str:
    """Create hash of URL for deduplication."""
    return hashlib.md5(url.encode()).hexdigest()


def is_duplicate(url: str, state: Dict, dedup_hours: int = 72) -> bool:
    """Check if URL was recently alerted."""
    url_hash = hash_url(url)
    dedup_map = state.get("deduplication", {}).get("url_hash_map", {})
    
    if url_hash not in dedup_map:
        return False
    
    # Check if within deduplication window
    last_seen_str = dedup_map[url_hash]
    last_seen = datetime.fromisoformat(last_seen_str)
    age = datetime.now() - last_seen
    
    return age < timedelta(hours=dedup_hours)


def mark_as_seen(url: str, state: Dict):
    """Mark URL as seen in deduplication map."""
    url_hash = hash_url(url)
    if "deduplication" not in state:
        state["deduplication"] = {"url_hash_map": {}}
    
    state["deduplication"]["url_hash_map"][url_hash] = datetime.now().isoformat()


def search_topic(topic: Dict, dry_run: bool = False) -> List[Dict]:
    """
    Search for topic using available search tools.
    
    In real Moltbot environment, this would use web_search tool.
    For standalone testing, returns mock results.
    """
    query = topic.get("query", "")
    
    # Try to use web-search-plus if available
    web_search_plus = Path(__file__).parent.parent.parent / "web-search-plus" / "scripts" / "search.py"
    
    if web_search_plus.exists():
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(web_search_plus), "-q", query, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("results", [])
        except Exception as e:
            print(f"⚠️ web-search-plus failed: {e}", file=sys.stderr)
    
    # Fallback: Return mock results for testing
    if dry_run:
        return [
            {
                "title": f"Mock result for {query}",
                "url": f"https://example.com/mock-{hashlib.md5(query.encode()).hexdigest()[:8]}",
                "snippet": f"This is a test result for query: {query}",
                "published_date": datetime.now().isoformat()
            }
        ]
    
    return []


def should_check_topic(topic: Dict, state: Dict, force: bool = False) -> bool:
    """Determine if topic should be checked now."""
    if force:
        return True
    
    topic_id = topic.get("id")
    frequency = topic.get("frequency", "daily")
    
    # Get last check time
    topic_state = state.get("topics", {}).get(topic_id, {})
    last_check_str = topic_state.get("last_check")
    
    if not last_check_str:
        return True  # Never checked
    
    last_check = datetime.fromisoformat(last_check_str)
    now = datetime.now()
    
    # Check frequency
    if frequency == "hourly":
        return (now - last_check) >= timedelta(hours=1)
    elif frequency == "daily":
        return (now - last_check) >= timedelta(days=1)
    elif frequency == "weekly":
        return (now - last_check) >= timedelta(weeks=1)
    
    return False


def check_rate_limits(topic: Dict, state: Dict, settings: Dict) -> bool:
    """Check if we've hit rate limits."""
    topic_id = topic.get("id")
    max_per_day = settings.get("max_alerts_per_day", 5)
    max_per_topic_per_day = settings.get("max_alerts_per_topic_per_day", 2)
    
    topic_state = state.get("topics", {}).get(topic_id, {})
    alerts_today = topic_state.get("alerts_today", 0)
    
    # Check topic limit
    if alerts_today >= max_per_topic_per_day:
        return False
    
    # Check global limit (count across all topics)
    total_alerts_today = sum(
        s.get("alerts_today", 0) 
        for s in state.get("topics", {}).values()
    )
    
    if total_alerts_today >= max_per_day:
        return False
    
    return True


def send_alert(topic: Dict, result: Dict, priority: str, score: float, reason: str, dry_run: bool = False):
    """Send alert via configured channels."""
    channels = topic.get("channels", [])
    
    # Build message
    emoji_map = {"high": "🔥", "medium": "📌", "low": "📝"}
    emoji = emoji_map.get(priority, "📌")
    
    topic_name = topic.get("name", "Research Alert")
    topic_emoji = topic.get("emoji", "🔍")
    context = topic.get("context", "")
    
    message = f"{emoji} **{topic_name}** {topic_emoji}\n\n"
    message += f"**{result['title']}**\n\n"
    message += f"{result.get('snippet', '')}\n\n"
    
    if context:
        message += f"💡 *Context:* {context}\n\n"
    
    message += f"🔗 {result['url']}\n\n"
    message += f"_Score: {score:.2f} | {reason}_"
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Would send alert:")
        print(f"Channels: {', '.join(channels)}")
        print(f"Priority: {priority.upper()}")
        print(f"\n{message}")
        print(f"{'='*60}\n")
        return
    
    # Send to channels
    for channel in channels:
        if channel == "telegram":
            send_telegram(message, priority)
        elif channel == "discord":
            send_discord(message, priority)
        elif channel == "email":
            send_email(message, priority, topic_name)


def send_telegram(message: str, priority: str):
    """Send via Telegram (requires Moltbot message tool)."""
    # In real environment, this would use Moltbot's message tool
    # For now, just log
    print(f"📱 [TELEGRAM] {priority.upper()}: {message[:100]}...")


def send_discord(message: str, priority: str):
    """Send via Discord webhook."""
    import requests
    from config import get_channel_config
    
    discord_config = get_channel_config("discord")
    webhook_url = discord_config.get("webhook_url")
    
    if not webhook_url:
        print("⚠️ Discord webhook not configured", file=sys.stderr)
        return
    
    payload = {
        "username": discord_config.get("username", "Research Bot"),
        "avatar_url": discord_config.get("avatar_url"),
        "content": message
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
        print(f"✅ Sent to Discord")
    except Exception as e:
        print(f"❌ Discord send failed: {e}", file=sys.stderr)


def send_email(message: str, priority: str, subject: str):
    """Send via email."""
    print(f"📧 [EMAIL] {priority.upper()}: {subject}")


def monitor_topic(topic: Dict, state: Dict, settings: Dict, dry_run: bool = False, verbose: bool = False):
    """Monitor a single topic."""
    topic_id = topic.get("id")
    topic_name = topic.get("name")
    
    if verbose:
        print(f"\n🔍 Checking topic: {topic_name} ({topic_id})")
    
    # Search
    results = search_topic(topic, dry_run=dry_run)
    
    if verbose:
        print(f"   Found {len(results)} results")
    
    # Score and filter
    dedup_hours = settings.get("deduplication_window_hours", 72)
    high_priority = []
    medium_priority = []
    
    for result in results:
        url = result.get("url", "")
        
        # Check deduplication
        if is_duplicate(url, state, dedup_hours):
            if verbose:
                print(f"   ⏭️  Skipping duplicate: {url}")
            continue
        
        # Score
        priority, score, reason = score_result(result, topic, settings)
        
        if verbose:
            print(f"   {priority.upper():6} ({score:.2f}) - {result.get('title', '')[:50]}...")
        
        # Categorize
        if priority == "high":
            high_priority.append((result, score, reason))
        elif priority == "medium":
            medium_priority.append((result, score, reason))
        
        # Mark as seen
        mark_as_seen(url, state)
    
    # Send high priority alerts
    for result, score, reason in high_priority:
        if check_rate_limits(topic, state, settings):
            send_alert(topic, result, "high", score, reason, dry_run=dry_run)
            
            # Increment alert counter
            if not dry_run:
                if "topics" not in state:
                    state["topics"] = {}
                if topic_id not in state["topics"]:
                    state["topics"][topic_id] = {}
                
                state["topics"][topic_id]["alerts_today"] = \
                    state["topics"][topic_id].get("alerts_today", 0) + 1
        else:
            if verbose:
                print(f"   ⚠️ Rate limit reached, skipping alert")
    
    # Save medium priority to findings
    date_str = datetime.now().strftime("%Y-%m-%d")
    for result, score, reason in medium_priority:
        if not dry_run:
            save_finding(topic_id, date_str, {
                "result": result,
                "score": score,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        
        if verbose:
            print(f"   💾 Saved to digest: {result.get('title', '')[:50]}...")
    
    # Update topic state
    if not dry_run:
        if "topics" not in state:
            state["topics"] = {}
        if topic_id not in state["topics"]:
            state["topics"][topic_id] = {}
        
        state["topics"][topic_id]["last_check"] = datetime.now().isoformat()
        state["topics"][topic_id]["last_results_count"] = len(results)
        state["topics"][topic_id]["findings_count"] = \
            state["topics"][topic_id].get("findings_count", 0) + len(medium_priority)


def main():
    parser = argparse.ArgumentParser(description="Monitor research topics")
    parser.add_argument("--dry-run", action="store_true", help="Don't send alerts or save state")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--topic", help="Check specific topic by ID")
    parser.add_argument("--force", action="store_true", help="Force check even if not due")
    parser.add_argument("--frequency", choices=["hourly", "daily", "weekly"], 
                       help="Only check topics with this frequency")
    
    args = parser.parse_args()
    
    # Load config and state
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    state = load_state()
    settings = get_settings()
    topics = config.get("topics", [])
    
    if not topics:
        print("⚠️ No topics configured", file=sys.stderr)
        sys.exit(0)
    
    # Filter topics
    topics_to_check = []
    
    for topic in topics:
        # Filter by specific topic
        if args.topic and topic.get("id") != args.topic:
            continue
        
        # Filter by frequency
        if args.frequency and topic.get("frequency") != args.frequency:
            continue
        
        # Check if due
        if should_check_topic(topic, state, force=args.force):
            topics_to_check.append(topic)
    
    if not topics_to_check:
        if args.verbose:
            print("✅ No topics due for checking")
        sys.exit(0)
    
    print(f"🔍 Monitoring {len(topics_to_check)} topic(s)...")
    
    # Monitor each topic
    for topic in topics_to_check:
        try:
            monitor_topic(topic, state, settings, dry_run=args.dry_run, verbose=args.verbose)
        except Exception as e:
            print(f"❌ Error monitoring {topic.get('name')}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Save state
    if not args.dry_run:
        save_state(state)
        print("✅ State saved")
    
    print("✅ Monitoring complete")


if __name__ == "__main__":
    main()
