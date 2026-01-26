#!/usr/bin/env python3
"""
Set up cron jobs to monitor token usage.
Run this once to enable automatic prompt archiving.
"""

import subprocess
import json

def setup_heartbeat_check():
    """Add token check to HEARTBEAT.md"""
    hb_path = Path.home() / ".clawd" / "HEARTBEAT.md"
    
    heartbeat_entry = """
### 🧠 Token Usage & Archive (Every Session)
- Run `python skills/remember-all-prompts-daily/scripts/check_token_usage.py`
- If usage > 95%: exports current session to archive
- If usage < 5%: fresh session, ready to ingest previous context
"""
    
    if hb_path.exists():
        content = hb_path.read_text()
        if "Token Usage & Archive" not in content:
            hb_path.write_text(content + "\n" + heartbeat_entry)
            print(f"✅ Added to {hb_path}")
    else:
        hb_path.write_text(heartbeat_entry)
        print(f"✅ Created {hb_path}")

def setup_cron_job():
    """Set up optional cron job for periodic checks"""
    cron_job = {
        "name": "remember-all-prompts-check",
        "text": "Check token usage and export if approaching limit",
        "schedule": "*/15 * * * *",  # Every 15 minutes
        "enabled": False  # Default to disabled, user can enable
    }
    
    print("\n📋 Optional Cron Job Config:")
    print(json.dumps(cron_job, indent=2))
    print("\nTo enable periodic checks, run:")
    print("  clawdbot cron add --text 'Token usage check' --schedule '*/15 * * * *'")

if __name__ == "__main__":
    from pathlib import Path
    
    print("🔧 Setting up Remember All Prompts Daily...\n")
    
    # Create memory directory if needed
    memory_dir = Path.home() / ".clawd" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Memory directory: {memory_dir}")
    
    # Setup heartbeat
    setup_heartbeat_check()
    
    # Show cron option
    setup_cron_job()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Heartbeat will check token usage automatically")
    print("2. At 95% usage: prompts will auto-export to memory/remember-all-prompts-daily.md")
    print("3. On new session: previous context will be available for ingestion")
    print("\nManual commands:")
    print("  python skills/remember-all-prompts-daily/scripts/export_prompts.py")
    print("  python skills/remember-all-prompts-daily/scripts/ingest_prompts.py")
    print("  python skills/remember-all-prompts-daily/scripts/check_token_usage.py")
