#!/usr/bin/env python3
"""
Setup cron jobs for proactive research monitoring.

Creates cron entries for:
- Hourly topic checks
- Daily topic checks
- Weekly digest
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, get_settings

SKILL_DIR = Path(__file__).parent.parent
MONITOR_SCRIPT = SKILL_DIR / "scripts" / "monitor.py"
DIGEST_SCRIPT = SKILL_DIR / "scripts" / "digest.py"


def get_current_crontab() -> str:
    """Get current user's crontab."""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def set_crontab(content: str):
    """Set user's crontab."""
    subprocess.run(
        ["crontab", "-"],
        input=content,
        text=True,
        check=True
    )


def remove_old_entries(crontab: str) -> str:
    """Remove old proactive-research cron entries."""
    lines = crontab.split("\n")
    filtered = [
        line for line in lines
        if "proactive-research" not in line.lower()
    ]
    return "\n".join(filtered)


def generate_cron_entries(settings: dict) -> list[str]:
    """Generate cron entries based on settings."""
    entries = []
    
    # Header
    entries.append("# Proactive Research - Auto-generated")
    
    # Hourly check (every hour)
    entries.append(
        f"0 * * * * cd {SKILL_DIR} && /usr/bin/python3 {MONITOR_SCRIPT} --frequency hourly"
    )
    
    # Daily check (9 AM)
    entries.append(
        f"0 9 * * * cd {SKILL_DIR} && /usr/bin/python3 {MONITOR_SCRIPT} --frequency daily"
    )
    
    # Weekly check (Sunday 9 AM)
    entries.append(
        f"0 9 * * 0 cd {SKILL_DIR} && /usr/bin/python3 {MONITOR_SCRIPT} --frequency weekly"
    )
    
    # Weekly digest
    digest_day = settings.get("digest_day", "sunday")
    digest_time = settings.get("digest_time", "18:00")
    
    # Parse time
    hour, minute = digest_time.split(":")
    
    # Parse day
    day_map = {
        "sunday": "0", "monday": "1", "tuesday": "2", "wednesday": "3",
        "thursday": "4", "friday": "5", "saturday": "6"
    }
    day_num = day_map.get(digest_day.lower(), "0")
    
    entries.append(
        f"{minute} {hour} * * {day_num} cd {SKILL_DIR} && /usr/bin/python3 {DIGEST_SCRIPT} --send"
    )
    
    return entries


def setup_cron(auto: bool = False):
    """Setup cron jobs."""
    print("🔧 Setting up proactive research cron jobs...\n")
    
    # Load config
    try:
        config = load_config()
        settings = get_settings()
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get current crontab
    current = get_current_crontab()
    
    # Remove old entries
    cleaned = remove_old_entries(current)
    
    # Generate new entries
    new_entries = generate_cron_entries(settings)
    
    # Preview
    print("The following cron jobs will be added:\n")
    for entry in new_entries:
        if not entry.startswith("#"):
            print(f"  {entry}")
    print()
    
    # Confirm
    if not auto:
        response = input("Continue? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Aborted")
            sys.exit(0)
    
    # Build new crontab
    new_crontab = cleaned.strip()
    if new_crontab:
        new_crontab += "\n\n"
    
    new_crontab += "\n".join(new_entries) + "\n"
    
    # Set crontab
    try:
        set_crontab(new_crontab)
        print("✅ Cron jobs installed successfully")
        print("\nTo verify, run: crontab -l")
    except Exception as e:
        print(f"❌ Failed to install cron jobs: {e}", file=sys.stderr)
        sys.exit(1)


def remove_cron():
    """Remove all proactive-research cron jobs."""
    print("🗑️  Removing proactive research cron jobs...\n")
    
    # Get current crontab
    current = get_current_crontab()
    
    # Remove entries
    cleaned = remove_old_entries(current)
    
    if cleaned == current:
        print("⚠️ No proactive-research cron jobs found")
        return
    
    # Set crontab
    try:
        set_crontab(cleaned)
        print("✅ Cron jobs removed successfully")
    except Exception as e:
        print(f"❌ Failed to remove cron jobs: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup cron jobs for proactive research")
    parser.add_argument("--auto", action="store_true", help="Auto-setup without confirmation")
    parser.add_argument("--remove", action="store_true", help="Remove cron jobs")
    
    args = parser.parse_args()
    
    if args.remove:
        remove_cron()
    else:
        setup_cron(auto=args.auto)


if __name__ == "__main__":
    main()
