#!/usr/bin/env python3
"""
Live Match Monitor - Checks for live matches and outputs alerts.

Uses ESPN API for real-time events including:
- ⚽ Goals with scorer names
- 🟥 Red cards
- ⏸️ Halftime
- 🏁 Full-time results

Run via cron during match windows. Only outputs when there are new events.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from espn import find_team_match, get_match_events, FOOTBALL_LEAGUES
from config import get_teams, get_alert_settings

STATE_FILE = Path(__file__).parent.parent / ".live_state.json"

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def check_team(team: dict, state: dict, alerts_config: dict) -> tuple[list, dict]:
    """Check a single team for updates. Returns (alerts, updated_state)."""
    alerts = []
    team_name = team.get("name", "Unknown")
    team_emoji = team.get("emoji", "⚽")
    espn_id = team.get("espn_id")
    
    if not espn_id:
        return [], state  # Skip teams without ESPN ID
    
    leagues = team.get("espn_leagues", ["eng.1", "uefa.champions"])
    match = find_team_match(espn_id, leagues)
    
    if not match:
        return [], state
    
    event = match["event"]
    event_id = str(match["event_id"])
    league = match["league"]
    
    status = event.get("status", {}).get("type", {}).get("description", "")
    
    # Get scores
    competitions = event.get("competitions", [{}])[0]
    competitors = competitions.get("competitors", [])
    
    home_team = away_team = ""
    home_score = away_score = 0
    is_home = False
    
    for c in competitors:
        t_name = c.get("team", {}).get("displayName", "?")
        t_id = str(c.get("team", {}).get("id", ""))
        score = int(c.get("score", 0) or 0)
        
        if c.get("homeAway") == "home":
            home_team, home_score = t_name, score
            if t_id == espn_id:
                is_home = True
        else:
            away_team, away_score = t_name, score
    
    # Previous state for this match
    prev = state.get(event_id, {})
    prev_status = prev.get("status", "")
    prev_events = set(prev.get("event_ids", []))
    
    # Kick-off
    if alerts_config.get("kickoff", True):
        if status == "In Progress" and prev_status != "In Progress":
            opponent = away_team if is_home else home_team
            alerts.append(f"🏟️ **KICK OFF!** {team_emoji}\n{home_team} vs {away_team}\n{FOOTBALL_LEAGUES.get(league, league)}")
    
    # Get detailed events
    try:
        key_events = get_match_events(event_id, "soccer", league)
    except:
        key_events = []
    
    current_event_ids = []
    
    for e in key_events:
        e_id = str(e.get("id", e.get("clock", {}).get("value", "")))
        current_event_ids.append(e_id)
        
        if e_id in prev_events:
            continue  # Already seen
        
        event_type = e.get("type", {}).get("text", "")
        clock = e.get("clock", {}).get("displayValue", "?'")
        e_team = e.get("team", {}).get("displayName", "")
        
        participants = e.get("participants", [])
        player = participants[0].get("athlete", {}).get("displayName", "Unknown") if participants else "Unknown"
        
        is_our_team = team_name.lower() in e_team.lower()
        
        # Goals
        if "Goal" in event_type and alerts_config.get("goals", True):
            emoji = "🎉" if is_our_team else "😬"
            score_line = f"{home_team} {home_score}-{away_score} {away_team}"
            
            if "Own Goal" in event_type:
                alerts.append(f"{emoji} **OWN GOAL!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
            elif "Penalty" in event_type:
                alerts.append(f"{emoji} **PENALTY!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
            else:
                alerts.append(f"{emoji} **GOAL!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
        
        # Red cards
        elif "Red" in event_type and alerts_config.get("red_cards", True):
            emoji = "😱" if is_our_team else "😈"
            alerts.append(f"{emoji} 🟥 **RED CARD!** {clock}\n{player} ({e_team})")
    
    # Halftime
    if alerts_config.get("halftime", True):
        if status == "Halftime" and prev_status != "Halftime":
            alerts.append(f"⏸️ **HALFTIME** {team_emoji}\n{home_team} {home_score}-{away_score} {away_team}")
    
    # Full time
    if alerts_config.get("fulltime", True):
        if status == "Final" and prev_status not in ("Final", ""):
            our_goals = home_score if is_home else away_score
            their_goals = away_score if is_home else home_score
            
            if our_goals > their_goals:
                result_emoji = "🎉✅"
                result = "WIN!"
            elif our_goals < their_goals:
                result_emoji = "😢❌"
                result = "LOSS"
            else:
                result_emoji = "🤝"
                result = "DRAW"
            
            alerts.append(f"🏁 **FULL TIME - {result}** {result_emoji} {team_emoji}\n{home_team} {home_score}-{away_score} {away_team}")
    
    # Update state
    state[event_id] = {
        "status": status,
        "home_score": home_score,
        "away_score": away_score,
        "event_ids": current_event_ids
    }
    
    return alerts, state

def check_all_teams() -> list:
    """Check all configured teams for updates."""
    all_alerts = []
    state = load_state()
    teams = get_teams()
    alerts_config = get_alert_settings()
    
    for team in teams:
        if not team.get("espn_id"):
            continue
        
        alerts, state = check_team(team, state, alerts_config)
        all_alerts.extend(alerts)
    
    save_state(state)
    return all_alerts

if __name__ == "__main__":
    alerts = check_all_teams()
    
    if alerts:
        for alert in alerts:
            print(alert)
            print("---")
    elif "--verbose" in sys.argv:
        print("No live updates.")
