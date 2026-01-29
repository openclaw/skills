---
name: simmer-weather
description: Trade Polymarket weather markets using NOAA forecasts via Simmer API. Inspired by gopfan2's $2M+ strategy. Use when user wants to trade temperature markets, automate weather bets, check NOAA forecasts, or run gopfan2-style trading.
metadata: {"clawdbot":{"emoji":"🌡️","requires":{"env":["SIMMER_API_KEY"]},"cron":"0 */2 * * *"}}
authors:
  - Simmer (@simmer_markets)
attribution: "Strategy inspired by gopfan2"
version: "1.3.0"
---

# Simmer Weather Trading

Trade temperature markets on Polymarket using NOAA forecast data.

## When to Use This Skill

Use this skill when the user wants to:
- Trade weather markets automatically
- Set up gopfan2-style temperature trading
- Buy low on weather predictions
- Check their weather trading positions
- Configure trading thresholds or locations

## What's New in v1.2.0

- **Max Trades Per Run**: New `SIMMER_WEATHER_MAX_TRADES` config to limit trades per scan cycle (default: 5)

### v1.1.1
- **Status Script**: New `scripts/status.py` for quick balance and position checks
- **API Reference**: Added Quick Commands section with API endpoints

### v1.1.0
- **Source Tagging**: All trades tagged with `sdk:weather` for portfolio tracking
- **Smart Sizing**: Position sizing based on available balance (`--smart-sizing`)
- **Context Safeguards**: Checks for flip-flop warnings, slippage, time decay
- **Price Trend Detection**: Detects recent price drops for stronger signals

## Setup Flow

When user asks to install or configure this skill:

1. **Ask for Simmer API key**
   - They can get it from simmer.markets/dashboard → SDK tab
   - Store in environment as `SIMMER_API_KEY`

2. **Ask about settings** (or confirm defaults)
   - Entry threshold: When to buy (default 15¢)
   - Exit threshold: When to sell (default 45¢)
   - Max position: Amount per trade (default $2.00)
   - Locations: Which cities to trade (default NYC)

3. **Save settings to environment variables**

4. **Set up cron** (runs every 2 hours by default)

## Configuration

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Entry threshold | `SIMMER_WEATHER_ENTRY` | 0.15 | Buy when price below this |
| Exit threshold | `SIMMER_WEATHER_EXIT` | 0.45 | Sell when price above this |
| Max position | `SIMMER_WEATHER_MAX_POSITION` | 2.00 | Maximum USD per trade |
| Max trades/run | `SIMMER_WEATHER_MAX_TRADES` | 5 | Maximum trades per scan cycle |
| Locations | `SIMMER_WEATHER_LOCATIONS` | NYC | Comma-separated cities |
| Smart sizing % | `SIMMER_WEATHER_SIZING_PCT` | 0.05 | % of balance per trade |

**Supported locations:** NYC, Chicago, Seattle, Atlanta, Dallas, Miami

## Quick Commands

```bash
# Check account balance and positions
python scripts/status.py

# Detailed position list
python scripts/status.py --positions
```

**API Reference:**
- Base URL: `https://api.simmer.markets`
- Auth: `Authorization: Bearer $SIMMER_API_KEY`
- Portfolio: `GET /api/sdk/portfolio`
- Positions: `GET /api/sdk/positions`

## Running the Skill

```bash
# Standard scan
python weather_trader.py

# Dry run (no trades)
python weather_trader.py --dry-run

# With smart position sizing (uses portfolio balance)
python weather_trader.py --smart-sizing

# Check positions only
python weather_trader.py --positions

# View config
python weather_trader.py --config

# Disable safeguards (not recommended)
python weather_trader.py --no-safeguards

# Disable trend detection
python weather_trader.py --no-trends
```

## How It Works

Each cycle the script:
1. Fetches active weather markets from Simmer API
2. Groups markets by event (each temperature day is one event)
3. Parses event names to get location and date
4. Fetches NOAA forecast for that location/date
5. Finds the temperature bucket that matches the forecast
6. **Safeguards**: Checks context for flip-flop warnings, slippage, time decay
7. **Trend Detection**: Looks for recent price drops (stronger buy signal)
8. **Entry**: If bucket price < threshold and safeguards pass → BUY
9. **Exit**: Checks open positions, sells if price > exit threshold
10. **Tagging**: All trades tagged with `sdk:weather` for tracking

## Smart Sizing

With `--smart-sizing`, position size is calculated as:
- 5% of available USDC balance (configurable via `SIMMER_WEATHER_SIZING_PCT`)
- Capped at 5x the max position setting
- Falls back to fixed size if portfolio unavailable

This prevents over-deployment and scales with your account size.

## Safeguards

Before trading, the skill checks:
- **Flip-flop warning**: Skips if you've been reversing too much
- **Slippage**: Skips if estimated slippage > 15%
- **Time decay**: Skips if market resolves in < 2 hours
- **Market status**: Skips if market already resolved

Disable with `--no-safeguards` (not recommended).

## Source Tagging

All trades are tagged with `source: "sdk:weather"`. This means:
- Portfolio shows breakdown by strategy
- Copytrading skill won't sell your weather positions
- You can track weather P&L separately

## Example Output

```
🌤️ Simmer Weather Trading Skill
==================================================

⚙️ Configuration:
  Entry threshold: 15% (buy below this)
  Exit threshold:  45% (sell above this)
  Max position:    $2.00
  Locations:       NYC
  Smart sizing:    ✓ Enabled
  Safeguards:      ✓ Enabled
  Trend detection: ✓ Enabled

💰 Portfolio:
  Balance: $150.00
  Exposure: $45.00
  Positions: 8

📍 NYC 2026-01-28 (high temp)
  NOAA forecast: 34°F
  Matching bucket: 34-35°F @ $0.12
  💡 Smart sizing: $7.50 (5% of $150.00 balance)
  ✅ Below threshold ($0.15) - BUY opportunity! 📉 (dropped 15% in 24h)
  Executing trade...
  ✅ Bought 62.5 shares @ $0.12

📊 Summary:
  Events scanned: 12
  Entry opportunities: 1
  Trades executed: 1
```

## Troubleshooting

**"Safeguard blocked: Severe flip-flop warning"**
- You've been changing direction too much on this market
- Wait before trading again

**"Slippage too high"**
- Market is illiquid, reduce position size or skip

**"Resolves in Xh - too soon"**
- Market resolving soon, risk is elevated

**"No weather markets found"**
- Weather markets may not be active (seasonal)

**"API key invalid"**
- Get new key from simmer.markets/dashboard → SDK tab
