#!/usr/bin/env python3
"""
Sports Ticker - Display results and upcoming fixtures for your teams.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from espn import find_team_match, format_match, get_scoreboard, FOOTBALL_LEAGUES
from config import get_teams

def team_ticker(team: dict) -> str:
    """Generate ticker for a single team."""
    lines = []
    name = team.get("name", "Unknown")
    emoji = team.get("emoji", "⚽")
    espn_id = team.get("espn_id")
    leagues = team.get("espn_leagues", ["eng.1"])
    
    lines.append(f"{emoji} **{name}**\n")
    
    if espn_id:
        match = find_team_match(espn_id, leagues)
        if match:
            lines.append(format_match(match["event"], include_events=True, 
                                     sport="soccer", league=match["league"]))
        else:
            lines.append("No upcoming match in scoreboard.")
    else:
        lines.append("(ESPN ID not configured)")
    
    return "\n".join(lines)

def all_teams_ticker() -> str:
    """Generate ticker for all configured teams."""
    teams = get_teams()
    
    if not teams:
        return "No teams configured. Copy config.example.json to config.json and add your teams!"
    
    parts = []
    for team in teams:
        if team.get("espn_id"):  # Only show teams with ESPN ID
            parts.append(team_ticker(team))
    
    if not parts:
        return "No teams with ESPN IDs configured."
    
    return ("\n" + "─" * 30 + "\n").join(parts)

def league_ticker(league: str = "eng.1") -> str:
    """Show all matches in a league."""
    lines = [f"**{FOOTBALL_LEAGUES.get(league, league)}**\n"]
    
    data = get_scoreboard("soccer", league)
    events = data.get("events", [])
    
    if not events:
        lines.append("No matches in scoreboard.")
    else:
        for event in events:
            lines.append(format_match(event, include_events=False))
            lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: show all configured teams
        print(all_teams_ticker())
    else:
        cmd = sys.argv[1]
        
        if cmd == "league":
            league = sys.argv[2] if len(sys.argv) > 2 else "eng.1"
            print(league_ticker(league))
        elif cmd == "all":
            print(all_teams_ticker())
        else:
            # Assume it's a team name
            teams = get_teams()
            team_lower = cmd.lower()
            for team in teams:
                if team_lower in team.get("name", "").lower() or team_lower in team.get("short_name", "").lower():
                    print(team_ticker(team))
                    break
            else:
                print(f"Team '{cmd}' not found in config.")
