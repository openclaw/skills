#!/usr/bin/env python3
"""Configuration handler for sports-ticker."""

import json
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
CONFIG_EXAMPLE = SKILL_DIR / "config.example.json"

def load_config() -> dict:
    """Load configuration from config.json."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    elif CONFIG_EXAMPLE.exists():
        print(f"⚠️  No config.json found. Copy config.example.json to config.json and customize it.")
        return json.loads(CONFIG_EXAMPLE.read_text())
    else:
        return {"teams": [], "alerts": {}}

def save_config(config: dict):
    """Save configuration to config.json."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

def get_teams() -> list:
    """Get list of enabled teams."""
    config = load_config()
    return [t for t in config.get("teams", []) if t.get("enabled", True)]

def get_team_by_name(name: str) -> Optional[dict]:
    """Find a team by name (case-insensitive)."""
    name_lower = name.lower()
    for team in get_teams():
        if name_lower in team.get("name", "").lower() or name_lower in team.get("short_name", "").lower():
            return team
    return None

def get_alert_settings() -> dict:
    """Get alert configuration."""
    config = load_config()
    return config.get("alerts", {
        "goals": True,
        "red_cards": True,
        "halftime": True,
        "fulltime": True,
        "kickoff": True
    })

def add_team(name: str, espn_id: str = None, thesportsdb_id: str = None, 
             leagues: list = None, emoji: str = "⚽", short_name: str = None):
    """Add a team to config."""
    config = load_config()
    
    team = {
        "name": name,
        "short_name": short_name or name.split()[0],
        "emoji": emoji,
        "enabled": True
    }
    
    if espn_id:
        team["espn_id"] = espn_id
        team["espn_leagues"] = leagues or ["eng.1", "uefa.champions"]
    
    if thesportsdb_id:
        team["thesportsdb_id"] = thesportsdb_id
    
    config.setdefault("teams", []).append(team)
    save_config(config)
    print(f"✅ Added {name} to config.json")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Config Manager")
        print("\nUsage:")
        print("  config.py show       - Show current config")
        print("  config.py teams      - List configured teams")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "show":
        print(json.dumps(load_config(), indent=2))
    elif cmd == "teams":
        teams = get_teams()
        print(f"Configured teams ({len(teams)}):\n")
        for t in teams:
            emoji = t.get("emoji", "⚽")
            name = t.get("name")
            espn = t.get("espn_id", "-")
            tsdb = t.get("thesportsdb_id", "-")
            print(f"  {emoji} {name:25} ESPN:{espn:6} TSDB:{tsdb}")
