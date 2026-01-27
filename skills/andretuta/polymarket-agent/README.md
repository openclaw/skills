# Polymarket Agent

🎰 AI-powered prediction market assistant for Clawdbot.

## What This Does

This skill transforms Clawdbot into a prediction market analyst that:

- **Searches markets** on Polymarket
- **Researches news** about market events
- **Compares odds** with real-world probability
- **Identifies opportunities** with edge
- **Executes trades** when you approve

## Quick Start

```bash
# Setup (configure your wallet)
poly setup

# Check everything works
poly doctor

# See active markets
poly markets --limit 10
```

## Usage with Clawdbot

Just ask naturally:

- *"Analyze Polymarket opportunities"*
- *"What should I bet on?"*
- *"Any good crypto markets?"*
- *"Search for Bitcoin markets"*
- *"Check my balance"*

The AI will search markets, research news, and give you recommendations.

## Requirements

- Python 3.9+
- Polygon wallet with USDC
- Clawdbot installed

## CLI Commands

| Command | Description |
|---------|-------------|
| `poly setup` | Configure wallet |
| `poly doctor` | Health check |
| `poly markets` | List markets |
| `poly balance` | Check USDC balance |
| `poly buy` | Place buy order |
| `poly sell` | Place sell order |

## License

MIT
