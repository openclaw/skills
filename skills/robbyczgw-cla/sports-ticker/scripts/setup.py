#!/usr/bin/env python3
"""
Setup helper for sports-ticker.

Helps you find team IDs and configure your teams.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from espn import search_team, get_scoreboard, FOOTBALL_LEAGUES
from config import add_team, load_config, save_config, CONFIG_FILE, CONFIG_EXAMPLE

def interactive_setup():
    """Interactive setup wizard."""
    print("🏆 Sports Ticker Setup\n")
    print("This will help you configure your teams.\n")
    
    # Create config if doesn't exist
    if not CONFIG_FILE.exists() and CONFIG_EXAMPLE.exists():
        import shutil
        shutil.copy(CONFIG_EXAMPLE, CONFIG_FILE)
        # Clear example teams
        config = load_config()
        config["teams"] = []
        save_config(config)
        print("✅ Created config.json\n")
    
    while True:
        print("\nOptions:")
        print("  1. Search for a team")
        print("  2. Add a team by ESPN ID")
        print("  3. Show current teams")
        print("  4. Done")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            name = input("Team name to search: ").strip()
            if name:
                print(f"\nSearching for '{name}'...\n")
                results = search_team(name)
                if results:
                    seen = set()
                    for r in results:
                        key = (r['id'], r['name'])
                        if key not in seen:
                            seen.add(key)
                            print(f"  ID: {r['id']:6} | {r['name']:30} | {r['league_name']}")
                else:
                    print("No results. Try a different name or check if the league is in today's scoreboard.")
        
        elif choice == "2":
            name = input("Team name: ").strip()
            espn_id = input("ESPN ID: ").strip()
            emoji = input("Emoji (default ⚽): ").strip() or "⚽"
            leagues = input("Leagues (comma-separated, e.g. eng.1,uefa.champions): ").strip()
            leagues = [l.strip() for l in leagues.split(",")] if leagues else ["eng.1"]
            
            if name and espn_id:
                add_team(name, espn_id=espn_id, leagues=leagues, emoji=emoji)
        
        elif choice == "3":
            config = load_config()
            teams = config.get("teams", [])
            if teams:
                print(f"\nConfigured teams ({len(teams)}):")
                for t in teams:
                    print(f"  {t.get('emoji', '⚽')} {t.get('name')} (ESPN: {t.get('espn_id', 'N/A')})")
            else:
                print("\nNo teams configured yet.")
        
        elif choice == "4":
            print("\n✅ Setup complete! Run 'python3 scripts/ticker.py' to see your teams.")
            break

def find_team_id(team_name: str):
    """Search for a team's ESPN ID."""
    print(f"Searching for '{team_name}'...\n")
    
    results = search_team(team_name, list(FOOTBALL_LEAGUES.keys())[:10])
    
    if results:
        seen = set()
        print("Found:\n")
        for r in results:
            key = (r['id'], r['name'])
            if key not in seen:
                seen.add(key)
                print(f"  ESPN ID: {r['id']:6} | {r['name']:30} | {r['league_name']}")
    else:
        print("No teams found. Tips:")
        print("  - The team must have a match in today's/upcoming scoreboard")
        print("  - Try the official team name (e.g., 'Tottenham Hotspur' not 'Spurs')")
        print("  - Check available leagues with: python3 scripts/espn.py leagues")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        interactive_setup()
    elif sys.argv[1] == "find":
        if len(sys.argv) < 3:
            print("Usage: setup.py find <team_name>")
        else:
            find_team_id(" ".join(sys.argv[2:]))
    else:
        print("Usage:")
        print("  setup.py          - Interactive setup")
        print("  setup.py find <team> - Find team ESPN ID")
