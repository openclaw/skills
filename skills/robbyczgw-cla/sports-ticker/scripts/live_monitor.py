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
    sport = team.get("sport", "soccer")  # Default to soccer for backward compatibility
    
    if not espn_id:
        return [], state  # Skip teams without ESPN ID
    
    leagues = team.get("espn_leagues", ["eng.1", "uefa.champions"])
    match = find_team_match(espn_id, leagues, sport)
    
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
        # Safely parse score - ESPN returns string, empty string, or int
        raw_score = c.get("score", 0)
        try:
            score = int(raw_score) if raw_score not in (None, "", "-") else 0
        except (ValueError, TypeError):
            score = 0
        
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
    
    # Kick-off / Game start
    if alerts_config.get("kickoff", True):
        # Check if game is live (covers "In Progress", "First Half", "Second Half", etc.)
        is_live = status in ("In Progress", "First Half", "Second Half", "1st Quarter", "2nd Quarter", 
                            "3rd Quarter", "4th Quarter", "1st Period", "2nd Period", "3rd Period")
        was_live = prev_status in ("In Progress", "First Half", "Second Half", "1st Quarter", "2nd Quarter",
                                   "3rd Quarter", "4th Quarter", "1st Period", "2nd Period", "3rd Period")
        
        if is_live and not was_live and prev_status != "Halftime":
            from espn import LEAGUES
            sport_leagues = LEAGUES.get(sport, {})
            opponent = away_team if is_home else home_team
            start_emoji = "🏟️" if sport == "soccer" else "🎮"
            start_text = "KICK OFF!" if sport == "soccer" else "GAME ON!"
            alerts.append(f"{start_emoji} **{start_text}** {team_emoji}\n{home_team} vs {away_team}\n{sport_leagues.get(league, league)}")
    
    # Get detailed events
    try:
        key_events = get_match_events(event_id, sport, league)
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
        
        # Scoring events (sport-specific)
        if alerts_config.get("goals", True):
            scored = False
            score_line = f"{home_team} {home_score}-{away_score} {away_team}"
            emoji = "🎉" if is_our_team else "😬"
            
            if sport == "soccer":
                if "Goal" in event_type:
                    scored = True
                    if "Own Goal" in event_type:
                        alerts.append(f"{emoji} **OWN GOAL!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
                    elif "Penalty" in event_type:
                        alerts.append(f"{emoji} **PENALTY!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
                    else:
                        alerts.append(f"{emoji} **GOAL!** {clock}\n⚽ {player} ({e_team})\n**{score_line}**")
            
            elif sport == "football":
                if "Touchdown" in event_type:
                    scored = True
                    alerts.append(f"{emoji} **TOUCHDOWN!** {clock}\n🏈 {player} ({e_team})\n**{score_line}**")
                elif "Field Goal" in event_type:
                    scored = True
                    alerts.append(f"{emoji} **FIELD GOAL!** {clock}\n🎯 {player} ({e_team})\n**{score_line}**")
            
            elif sport == "basketball":
                if "Three Point" in event_type or "3PT" in event_type:
                    scored = True
                    alerts.append(f"{emoji} **3-POINTER!** {clock}\n🎯 {player} ({e_team})\n**{score_line}**")
            
            elif sport == "hockey":
                if "Goal" in event_type:
                    scored = True
                    alerts.append(f"{emoji} **GOAL!** {clock}\n🏒 {player} ({e_team})\n**{score_line}**")
            
            elif sport == "baseball":
                if "Home Run" in event_type or "HR" in event_type:
                    scored = True
                    alerts.append(f"{emoji} **HOME RUN!** {clock}\n⚾ {player} ({e_team})\n**{score_line}**")
        
        # Red cards / Ejections (mainly for soccer and hockey)
        if alerts_config.get("red_cards", True):
            if sport == "soccer" and "Red" in event_type:
                emoji = "😱" if is_our_team else "😈"
                alerts.append(f"{emoji} 🟥 **RED CARD!** {clock}\n{player} ({e_team})")
            elif sport == "hockey" and "Major Penalty" in event_type:
                emoji = "😱" if is_our_team else "😈"
                alerts.append(f"{emoji} **MAJOR PENALTY!** {clock}\n{player} ({e_team})")
    
    # Halftime / Period breaks
    if alerts_config.get("halftime", True):
        if status == "Halftime" and prev_status != "Halftime":
            alerts.append(f"⏸️ **HALFTIME** {team_emoji}\n{home_team} {home_score}-{away_score} {away_team}")
        elif "End of" in status and "End of" not in prev_status:
            # Basketball/Hockey period breaks
            alerts.append(f"⏸️ **{status.upper()}** {team_emoji}\n{home_team} {home_score}-{away_score} {away_team}")
    
    # Full time / Final
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
            
            final_text = "FULL TIME" if sport == "soccer" else "FINAL"
            alerts.append(f"🏁 **{final_text} - {result}** {result_emoji} {team_emoji}\n{home_team} {home_score}-{away_score} {away_team}")
    
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
