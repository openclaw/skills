#!/usr/bin/env python3
"""
Export all prompts from current session to daily archive.
Triggered at 95% token usage or manually.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Import Clawdbot's session management (when available)
try:
    from clawdbot import sessions_history
    USE_CLAWDBOT_API = True
except ImportError:
    USE_CLAWDBOT_API = False

def get_session_history():
    """Fetch current session history."""
    if not USE_CLAWDBOT_API:
        # Fallback: try to read from local session cache
        return None
    
    try:
        # This would be called via Clawdbot's message passing
        history = sessions_history(sessionKey=None)  # Current session
        return history
    except Exception as e:
        print(f"Error fetching session history: {e}")
        return None

def format_message(msg, index):
    """Format a single message."""
    timestamp = datetime.fromisoformat(msg.get('timestamp', datetime.now().isoformat()))
    role = msg.get('role', 'unknown')
    text = msg.get('text', '').strip()
    
    # Truncate long responses for readability
    if len(text) > 500:
        text = text[:500] + f"\n... [truncated, {len(msg.get('text', ''))} chars total]"
    
    return f"""**[{index}] {role.upper()} @ {timestamp.strftime('%H:%M:%S')}**
{text}

"""

def export_to_archive(history, session_label=""):
    """Export history to daily archive file."""
    if not history:
        print("No history to export")
        return False
    
    archive_path = Path.home() / ".clawd" / "memory" / "remember-all-prompts-daily.md"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Format session content
    session_content = f"### Session {current_time} {session_label}\n\n"
    
    for idx, msg in enumerate(history, 1):
        session_content += format_message(msg, idx)
    
    # Check if file exists and if today's section exists
    existing_content = ""
    if archive_path.exists():
        existing_content = archive_path.read_text()
    
    # Check if today's date already has entries
    today_marker = f"## [DATE: {today}]"
    if today_marker not in existing_content:
        # New day, add date marker
        new_content = existing_content + f"\n{today_marker}\n\n" + session_content
    else:
        # Append to today's section
        parts = existing_content.split(today_marker)
        new_content = parts[0] + today_marker + parts[1] + session_content
    
    # Write back
    archive_path.write_text(new_content)
    
    print(f"✅ Exported {len(history)} messages to {archive_path}")
    print(f"📅 Archive: {archive_path}")
    print(f"⏰ Timestamp: {current_time}")
    
    return True

if __name__ == "__main__":
    import sys
    
    # Get session history via Clawdbot CLI if available
    session_label = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    # Try to fetch from Clawdbot
    print("Fetching current session history...")
    
    # For now, this is a template - in actual use, Clawdbot would call this
    # with session context passed in via environment or args
    
    history = get_session_history()
    if history:
        export_to_archive(history, session_label)
    else:
        print("⚠️  Session history API not available yet.")
        print("This script will be integrated with Clawdbot's session management.")
        print("For now, you can manually trigger this via:")
        print("  sessions_spawn --task 'export current session'")
