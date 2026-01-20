#!/usr/bin/env python3
"""
ESPN Sports API - FREE live scores with goal scorers, cards, and more!

No API key required. Works for:
- Football/Soccer (Premier League, Champions League, La Liga, Serie A, etc.)
- NFL, NBA, MLB, NHL (American sports)
- And many more...

Base URL: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}
"""

import urllib.request
import json
import sys
from typing import Optional
from pathlib import Path

# ESPN API Base
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# Common football/soccer leagues
FOOTBALL_LEAGUES = {
    # European
    "eng.1": "Premier League",
    "eng.2": "Championship",
    "esp.1": "La Liga",
    "ger.1": "Bundesliga",
    "ita.1": "Serie A",
    "fra.1": "Ligue 1",
    "ned.1": "Eredivisie",
    "por.1": "Primeira Liga",
    "aut.1": "Austrian Bundesliga",
    # European competitions
    "uefa.champions": "Champions League",
    "uefa.europa": "Europa League",
    "uefa.europa.conf": "Conference League",
    # Americas
    "usa.1": "MLS",
    "mex.1": "Liga MX",
    "bra.1": "Brasileirão",
    "arg.1": "Argentine Primera",
    # International
    "fifa.world": "World Cup",
    "uefa.euro": "Euros",
}

def api_request(endpoint: str) -> dict:
    """Make request to ESPN API (no auth needed!)."""
    url = f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def get_scoreboard(sport: str = "soccer", league: str = "eng.1") -> dict:
    """Get current scoreboard for a league."""
    return api_request(f"{sport}/{league}/scoreboard")

def get_match_details(event_id: str, sport: str = "soccer", league: str = "eng.1") -> dict:
    """Get detailed match info including events."""
    return api_request(f"{sport}/{league}/summary?event={event_id}")

def get_all_teams(league: str = "eng.1") -> list:
    """Get ALL teams in a league (not just today's matches)."""
    data = api_request(f"soccer/{league}/teams")
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    return [t.get("team", {}) for t in teams]

def search_team(team_name: str, leagues: list = None) -> list:
    """Search for a team across leagues using the teams endpoint."""
    if leagues is None:
        leagues = ["eng.1", "esp.1", "ger.1", "ita.1", "fra.1", "uefa.champions"]
    
    team_lower = team_name.lower()
    results = []
    
    for league in leagues:
        try:
            teams = get_all_teams(league)
            for team in teams:
                if team_lower in team.get("displayName", "").lower() or \
                   team_lower in team.get("shortDisplayName", "").lower() or \
                   team_lower in team.get("nickname", "").lower():
                    results.append({
                        "id": team.get("id"),
                        "name": team.get("displayName"),
                        "short": team.get("shortDisplayName"),
                        "league": league,
                        "league_name": FOOTBALL_LEAGUES.get(league, league)
                    })
        except Exception:
            continue
    
    return results

def find_team_match(team_id: str, leagues: list = None, sport: str = "soccer") -> Optional[dict]:
    """Find a match for a specific team."""
    if leagues is None:
        leagues = ["eng.1", "uefa.champions"]
    
    for league in leagues:
        try:
            data = get_scoreboard(sport, league)
            for event in data.get("events", []):
                for comp in event.get("competitions", []):
                    for competitor in comp.get("competitors", []):
                        if str(competitor.get("team", {}).get("id")) == str(team_id):
                            return {
                                "event": event,
                                "league": league,
                                "event_id": event.get("id"),
                                "sport": sport
                            }
        except Exception:
            continue
    
    return None

def get_match_events(event_id: str, sport: str = "soccer", league: str = "eng.1") -> list:
    """Get key events (goals, cards) from a match."""
    details = get_match_details(event_id, sport, league)
    return details.get("keyEvents", [])

def format_event(event: dict) -> str:
    """Format a match event for display."""
    event_type = event.get("type", {}).get("text", "")
    clock = event.get("clock", {}).get("displayValue", "?'")
    team = event.get("team", {}).get("displayName", "")
    
    participants = event.get("participants", [])
    player = participants[0].get("athlete", {}).get("displayName", "") if participants else ""
    
    if "Goal" in event_type:
        detail = ""
        if "Own Goal" in event_type:
            detail = " (OG)"
        elif "Penalty" in event_type:
            detail = " (pen)"
        return f"⚽ {clock} {player}{detail} ({team})"
    elif "Yellow" in event_type:
        return f"🟨 {clock} {player} ({team})"
    elif "Red" in event_type:
        return f"🟥 {clock} {player} ({team})"
    elif "Substitution" in event_type:
        return f"🔄 {clock} {player} ({team})"
    
    return f"📋 {clock} {event_type}: {player}"

def format_match(event: dict, include_events: bool = True, sport: str = "soccer", league: str = "eng.1") -> str:
    """Format a full match summary."""
    lines = []
    
    status = event.get("status", {})
    status_desc = status.get("type", {}).get("description", "Unknown")
    clock = status.get("displayClock", "")
    
    # Status header
    if status_desc == "In Progress":
        lines.append(f"🔴 LIVE {clock}")
    elif status_desc == "Halftime":
        lines.append("⏸️ HALFTIME")
    elif status_desc == "Final":
        lines.append("🏁 FULL TIME")
    else:
        lines.append(f"📅 {status_desc}")
    
    # Teams and score
    competitions = event.get("competitions", [{}])[0]
    competitors = competitions.get("competitors", [])
    
    home = away = ""
    home_score = away_score = "0"
    
    for c in competitors:
        team_name = c.get("team", {}).get("displayName", "?")
        score = c.get("score", "0")
        if c.get("homeAway") == "home":
            home, home_score = team_name, score
        else:
            away, away_score = team_name, score
    
    lines.append(f"**{home} {home_score} - {away_score} {away}**")
    
    # Events
    if include_events:
        event_id = event.get("id")
        if event_id:
            try:
                events = get_match_events(event_id, sport, league)
                if events:
                    lines.append("")
                    for e in events[-8:]:
                        lines.append(format_event(e))
            except Exception:
                pass
    
    return "\n".join(lines)

def list_leagues():
    """List available football leagues."""
    print("Available Football/Soccer Leagues:\n")
    for code, name in sorted(FOOTBALL_LEAGUES.items(), key=lambda x: x[1]):
        print(f"  {code:20} {name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ESPN Sports API - Free live data!")
        print("\nUsage:")
        print("  espn.py leagues              - List available leagues")
        print("  espn.py scoreboard [league]  - Get scoreboard (default: eng.1)")
        print("  espn.py search <team>        - Search for a team")
        print("  espn.py match <event_id> [league] - Get match details")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "leagues":
        list_leagues()
    
    elif cmd == "scoreboard":
        league = sys.argv[2] if len(sys.argv) > 2 else "eng.1"
        data = get_scoreboard("soccer", league)
        print(f"=== {FOOTBALL_LEAGUES.get(league, league)} ===\n")
        for event in data.get("events", []):
            print(format_match(event, include_events=False))
            print()
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: espn.py search <team_name>")
            sys.exit(1)
        team = " ".join(sys.argv[2:])
        results = search_team(team)
        if results:
            print(f"Found teams matching '{team}':\n")
            for r in results:
                print(f"  ID: {r['id']:6} | {r['name']:25} | {r['league_name']}")
        else:
            print(f"No teams found matching '{team}'")
    
    elif cmd == "match":
        if len(sys.argv) < 3:
            print("Usage: espn.py match <event_id> [league]")
            sys.exit(1)
        event_id = sys.argv[2]
        league = sys.argv[3] if len(sys.argv) > 3 else "eng.1"
        details = get_match_details(event_id, "soccer", league)
        event = details.get("header", {}).get("competitions", [{}])[0]
        # Reconstruct event format
        print(f"Match details for event {event_id}")
