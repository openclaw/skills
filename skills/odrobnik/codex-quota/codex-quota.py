#!/usr/bin/env python3
"""Check OpenAI Codex CLI rate limit status."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def find_latest_session_file():
    """Find the most recently modified session file."""
    sessions_dir = Path.home() / ".codex" / "sessions"
    now = datetime.now()
    
    for day_offset in range(2):
        date = datetime(now.year, now.month, now.day)
        date = datetime.fromordinal(date.toordinal() - day_offset)
        day_dir = sessions_dir / f"{date.year:04d}" / f"{date.month:02d}" / f"{date.day:02d}"
        
        if not day_dir.exists():
            continue
        
        jsonl_files = list(day_dir.glob("*.jsonl"))
        if jsonl_files:
            latest = max(jsonl_files, key=lambda f: f.stat().st_mtime)
            return latest
    
    return None

def extract_rate_limits(file_path):
    """Extract rate limits from the last token_count event in a session file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if (event.get('payload', {}).get('type') == 'token_count' and
                event.get('payload', {}).get('rate_limits')):
                return event['payload']['rate_limits']
        except json.JSONDecodeError:
            continue
    
    return None

def format_window(minutes):
    """Format window duration in human-readable form."""
    if minutes >= 1440:
        days = minutes // 1440
        return f"{days} day{'s' if days != 1 else ''}"
    elif minutes >= 60:
        hours = minutes // 60
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{minutes} min"

def format_reset_time(unix_timestamp):
    """Format reset time with countdown."""
    reset_dt = datetime.fromtimestamp(unix_timestamp)
    now = datetime.now()
    delta = reset_dt - now
    
    time_str = reset_dt.strftime("%Y-%m-%d %H:%M")
    
    if delta.total_seconds() > 0:
        hours = int(delta.total_seconds()) // 3600
        minutes = (int(delta.total_seconds()) % 3600) // 60
        if hours > 0:
            return f"{time_str} (in {hours}h {minutes}m)"
        else:
            return f"{time_str} (in {minutes}m)"
    else:
        return f"{time_str} (passed)"

def progress_bar(percent, width=20):
    """Generate a progress bar string."""
    filled = int((percent / 100.0) * width)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + "]"

def unix_to_iso(timestamp):
    """Convert Unix timestamp to ISO 8601 string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def file_mod_time_iso(file_path):
    """Get file modification time as ISO 8601 string."""
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def file_mod_time_local(file_path):
    """Get file modification time in local timezone."""
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

def output_json(limits, file_path):
    """Output rate limits as JSON."""
    output = {
        "primary": {
            "used_percent": limits['primary']['used_percent'],
            "window_minutes": limits['primary']['window_minutes'],
            "resets_at": unix_to_iso(limits['primary']['resets_at'])
        },
        "secondary": {
            "used_percent": limits['secondary']['used_percent'],
            "window_minutes": limits['secondary']['window_minutes'],
            "resets_at": unix_to_iso(limits['secondary']['resets_at'])
        },
        "updated_at": file_mod_time_iso(file_path)
    }
    print(json.dumps(output, indent=2))

def output_pretty(limits, file_path):
    """Output rate limits in human-readable format."""
    primary = limits['primary']
    secondary = limits['secondary']
    
    print()
    print("═══════════════════════════════════════════")
    print("           CODEX RATE LIMIT STATUS         ")
    print("═══════════════════════════════════════════")
    print()
    print(f"📊 Primary ({format_window(primary['window_minutes'])} window)")
    print(f"   {progress_bar(primary['used_percent'])} {primary['used_percent']:.1f}%")
    print(f"   Resets: {format_reset_time(primary['resets_at'])}")
    print()
    print(f"📈 Secondary ({format_window(secondary['window_minutes'])} window)")
    print(f"   {progress_bar(secondary['used_percent'])} {secondary['used_percent']:.1f}%")
    print(f"   Resets: {format_reset_time(secondary['resets_at'])}")
    print()
    print("═══════════════════════════════════════════")
    print(f"   Updated: {file_mod_time_local(file_path)}")
    print("═══════════════════════════════════════════")

def ping_codex():
    """Ping Codex to get fresh rate limit data."""
    import subprocess
    print("🔄 Pinging Codex for fresh rate limit data...")
    
    try:
        subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", "reply OK"],
            cwd=Path.home(),
            capture_output=True,
            timeout=60
        )
    except Exception as e:
        print(f"⚠️  Failed to ping Codex: {e}")
    
    import time
    time.sleep(0.5)
    return find_latest_session_file()

def main():
    args = set(sys.argv[1:])
    
    if "--help" in args or "-h" in args:
        print("""Usage: codex-quota.py [OPTIONS]

Shows OpenAI Codex rate limit status from session files.

Options:
  --fresh, -f    Ping Codex to get fresh rate limit data
  --json, -j     Output as JSON
  --help, -h     Show this help

By default, uses the most recent session file (cached data).""")
        return
    
    want_fresh = "--fresh" in args or "-f" in args
    want_json = "--json" in args or "-j" in args
    
    if want_fresh:
        session_file = ping_codex()
    else:
        session_file = find_latest_session_file()
    
    if not session_file:
        if want_json:
            print('{"error": "No session files found"}')
        else:
            print("❌ No session files found")
        sys.exit(1)
    
    limits = extract_rate_limits(session_file)
    
    if not limits:
        if want_json:
            print('{"error": "Could not extract rate limits"}')
        else:
            print("❌ Could not extract rate limits from session file")
            print(f"   File: {session_file}")
        sys.exit(1)
    
    if want_json:
        output_json(limits, session_file)
    else:
        output_pretty(limits, session_file)

if __name__ == "__main__":
    main()
