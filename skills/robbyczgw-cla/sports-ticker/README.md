# 🏆 Sports Ticker

**Live sports alerts with goal scorers, cards, and real-time updates — completely FREE!**

Built for [Clawdbot](https://clawdbot.com) but works standalone too.

## ✨ Features

- ⚽ **Live goal alerts** with scorer names and minute
- 🟥 **Red card alerts** with player names
- ⏸️ **Halftime** score updates
- 🏁 **Full-time** results with WIN/LOSS/DRAW
- 📊 **Multi-team support** — track as many teams as you want
- 🔄 **Auto-scheduling** — cron jobs for match days (Clawdbot)
- 💰 **100% FREE** — no API keys, no subscriptions!

## 🎯 The Secret Sauce: ESPN API

This skill uses ESPN's public API which provides:
- Real-time scores
- Goal scorers with timestamps
- Cards, substitutions
- Match statistics

**No API key required!** ESPN's API is open and free to use.

### Supported Leagues

| League | Code | Coverage |
|--------|------|----------|
| Premier League | `eng.1` | ✅ Full |
| Champions League | `uefa.champions` | ✅ Full |
| La Liga | `esp.1` | ✅ Full |
| Bundesliga | `ger.1` | ✅ Full |
| Serie A | `ita.1` | ✅ Full |
| Ligue 1 | `fra.1` | ✅ Full |
| Europa League | `uefa.europa` | ✅ Full |
| MLS | `usa.1` | ✅ Full |
| And 20+ more... | | |

## 🚀 Quick Start

### 1. Install

```bash
# Clone or copy to your skills directory
clawdhub install sports-ticker

# Or manually
git clone https://github.com/your-repo/sports-ticker
cd sports-ticker
```

### 2. Configure Your Teams

```bash
# Interactive setup
python3 scripts/setup.py

# Or find team IDs directly
python3 scripts/setup.py find "Tottenham"
python3 scripts/setup.py find "Barcelona"
```

Common team IDs for reference:
- Tottenham: 367, Arsenal: 359, Liverpool: 364, Man City: 382, Man United: 360
- Barcelona: 83, Real Madrid: 86, Bayern: 132, PSG: 160, Juventus: 111

### 3. Create config.json

```bash
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "teams": [
    {
      "name": "Liverpool",
      "short_name": "Liverpool",
      "emoji": "🔴",
      "espn_id": "364",
      "espn_leagues": ["eng.1", "uefa.champions"],
      "enabled": true
    }
  ],
  "alerts": {
    "goals": true,
    "red_cards": true,
    "halftime": true,
    "fulltime": true,
    "kickoff": true
  }
}
```

### 4. Test It

```bash
# Show ticker for your teams
python3 scripts/ticker.py

# Check live matches
python3 scripts/live_monitor.py --verbose

# View a specific league
python3 scripts/ticker.py league eng.1
```

## 📱 Example Alerts

**Goal scored:**
```
🎉 GOAL! 23'
⚽ Marcus Rashford (Manchester United)
Manchester United 1-0 Liverpool
```

**Red card:**
```
😈 🟥 RED CARD! 67'
Darwin Núñez (Liverpool)
```

**Full time:**
```
🏁 FULL TIME - WIN! 🎉✅ 🔴
Manchester United 2-1 Liverpool
```

## 🤖 Clawdbot Integration

### Auto-Scheduling (Match Day Alerts)

Create a daily cron job that checks for matches:

```javascript
// Morning check at 9 AM
{
  "name": "sports-match-check",
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "Europe/London" },
  "payload": {
    "message": "Check if any configured teams play today. If yes, create a live ticker cron for the match window."
  }
}
```

### Live Ticker Cron

During matches, run every 2 minutes:
```bash
python3 scripts/live_monitor.py
```

The script only outputs when there are new events (goals, cards, etc.), making it perfect for cron-based alerting.

## 🔧 Scripts Reference

| Script | Purpose |
|--------|---------|
| `ticker.py` | Show current status of your teams |
| `live_monitor.py` | Check for live updates (for cron) |
| `espn.py` | Direct ESPN API access |
| `setup.py` | Interactive setup wizard |
| `config.py` | Configuration management |

## 🌐 ESPN API Reference

Base URL: `https://site.api.espn.com/apis/site/v2/sports`

### Endpoints

```bash
# Scoreboard (all today's matches)
/soccer/{league}/scoreboard

# Match details with events
/soccer/{league}/summary?event={event_id}

# Team info
/soccer/{league}/teams/{team_id}
```

### League Codes

```
eng.1          Premier League
eng.2          Championship  
esp.1          La Liga
ger.1          Bundesliga
ita.1          Serie A
fra.1          Ligue 1
uefa.champions Champions League
uefa.europa    Europa League
usa.1          MLS
mex.1          Liga MX
```

## 📄 License

MIT — use it however you want!

## 🙏 Credits

- ESPN for their awesome (and free!) API
- [Public ESPN API Documentation](https://github.com/pseudo-r/Public-ESPN-API) by pseudo-r
- Built with ❤️ for football fans everywhere

---

**COYS! ⚽🏆**
