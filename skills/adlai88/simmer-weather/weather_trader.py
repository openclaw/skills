#!/usr/bin/env python3
"""
Simmer Weather Trading Skill

Trades Polymarket weather markets using NOAA forecasts.
Inspired by gopfan2's $2M+ weather trading strategy.

Usage:
    python weather_trader.py              # Run trading scan
    python weather_trader.py --dry-run    # Show opportunities without trading
    python weather_trader.py --positions  # Show current positions only
    python weather_trader.py --smart-sizing  # Use portfolio-based position sizing

Requires:
    SIMMER_API_KEY environment variable (get from simmer.markets/dashboard)
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

# =============================================================================
# Configuration
# =============================================================================

SIMMER_API_BASE = "https://api.simmer.markets"
NOAA_API_BASE = "https://api.weather.gov"

# Source tag for tracking
TRADE_SOURCE = "sdk:weather"

# Polymarket constraints
MIN_SHARES_PER_ORDER = 5.0  # Polymarket requires minimum 5 shares
MIN_TICK_SIZE = 0.01        # Minimum tradeable price

# Strategy parameters - configurable via environment variables
ENTRY_THRESHOLD = float(os.environ.get("SIMMER_WEATHER_ENTRY", "0.15"))
EXIT_THRESHOLD = float(os.environ.get("SIMMER_WEATHER_EXIT", "0.45"))
MAX_POSITION_USD = float(os.environ.get("SIMMER_WEATHER_MAX_POSITION", "2.00"))

# Smart sizing parameters
SMART_SIZING_PCT = float(os.environ.get("SIMMER_WEATHER_SIZING_PCT", "0.05"))  # 5% of available balance per trade

# Rate limiting
MAX_TRADES_PER_RUN = int(os.environ.get("SIMMER_WEATHER_MAX_TRADES", "5"))  # Max trades per scan cycle

# Context safeguard thresholds
SLIPPAGE_MAX_PCT = 0.15  # Skip if slippage > 15%
TIME_TO_RESOLUTION_MIN_HOURS = 2  # Skip if resolving in < 2 hours

# Price trend detection
PRICE_DROP_THRESHOLD = 0.10  # 10% drop in last 24h = stronger signal

# Supported locations (matching Polymarket resolution sources)
LOCATIONS = {
    "NYC": {"lat": 40.7769, "lon": -73.8740, "name": "New York City (LaGuardia)"},
    "Chicago": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago (O'Hare)"},
    "Seattle": {"lat": 47.4502, "lon": -122.3088, "name": "Seattle (Sea-Tac)"},
    "Atlanta": {"lat": 33.6407, "lon": -84.4277, "name": "Atlanta (Hartsfield)"},
    "Dallas": {"lat": 32.8998, "lon": -97.0403, "name": "Dallas (DFW)"},
    "Miami": {"lat": 25.7959, "lon": -80.2870, "name": "Miami (MIA)"},
}

# Active locations - configurable via environment
_locations_env = os.environ.get("SIMMER_WEATHER_LOCATIONS", "NYC")
ACTIVE_LOCATIONS = [loc.strip().upper() for loc in _locations_env.split(",") if loc.strip()]

# =============================================================================
# NOAA Weather API
# =============================================================================

def fetch_json(url, headers=None):
    """Fetch JSON from URL with error handling."""
    try:
        req = Request(url, headers=headers or {})
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        print(f"  HTTP Error {e.code}: {url}")
        return None
    except URLError as e:
        print(f"  URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def get_noaa_forecast(location: str) -> dict:
    """Get NOAA forecast for a location. Returns dict with date -> {"high": temp, "low": temp}"""
    if location not in LOCATIONS:
        print(f"  Unknown location: {location}")
        return {}

    loc = LOCATIONS[location]
    headers = {
        "User-Agent": "SimmerWeatherSkill/1.0 (https://simmer.markets)",
        "Accept": "application/geo+json",
    }

    points_url = f"{NOAA_API_BASE}/points/{loc['lat']},{loc['lon']}"
    points_data = fetch_json(points_url, headers)

    if not points_data or "properties" not in points_data:
        print(f"  Failed to get NOAA grid for {location}")
        return {}

    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        print(f"  No forecast URL for {location}")
        return {}

    forecast_data = fetch_json(forecast_url, headers)
    if not forecast_data or "properties" not in forecast_data:
        print(f"  Failed to get NOAA forecast for {location}")
        return {}

    periods = forecast_data["properties"].get("periods", [])
    forecasts = {}

    for period in periods:
        start_time = period.get("startTime", "")
        if not start_time:
            continue

        date_str = start_time[:10]
        temp = period.get("temperature")
        is_daytime = period.get("isDaytime", True)

        if date_str not in forecasts:
            forecasts[date_str] = {"high": None, "low": None}

        if is_daytime:
            forecasts[date_str]["high"] = temp
        else:
            forecasts[date_str]["low"] = temp

    return forecasts


# =============================================================================
# Market Parsing
# =============================================================================

def parse_weather_event(event_name: str) -> dict:
    """Parse weather event name to extract location, date, metric."""
    if not event_name:
        return None

    event_lower = event_name.lower()

    if 'highest' in event_lower or 'high temp' in event_lower:
        metric = 'high'
    elif 'lowest' in event_lower or 'low temp' in event_lower:
        metric = 'low'
    else:
        metric = 'high'

    location = None
    location_aliases = {
        'nyc': 'NYC', 'new york': 'NYC', 'laguardia': 'NYC', 'la guardia': 'NYC',
        'chicago': 'Chicago', "o'hare": 'Chicago', 'ohare': 'Chicago',
        'seattle': 'Seattle', 'sea-tac': 'Seattle',
        'atlanta': 'Atlanta', 'hartsfield': 'Atlanta',
        'dallas': 'Dallas', 'dfw': 'Dallas',
        'miami': 'Miami',
    }

    for alias, loc in location_aliases.items():
        if alias in event_lower:
            location = loc
            break

    if not location:
        return None

    month_day_match = re.search(r'on\s+([a-zA-Z]+)\s+(\d{1,2})', event_name, re.IGNORECASE)
    if not month_day_match:
        return None

    month_name = month_day_match.group(1).lower()
    day = int(month_day_match.group(2))

    month_map = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
    }

    month = month_map.get(month_name)
    if not month:
        return None

    now = datetime.now(timezone.utc)
    year = now.year
    try:
        target_date = datetime(year, month, day, tzinfo=timezone.utc)
        if target_date < now - timedelta(days=30):
            year += 1
        date_str = f"{year}-{month:02d}-{day:02d}"
    except ValueError:
        return None

    return {"location": location, "date": date_str, "metric": metric}


def parse_temperature_bucket(outcome_name: str) -> tuple:
    """Parse temperature bucket from outcome name."""
    if not outcome_name:
        return None

    below_match = re.search(r'(\d+)\s*°?[fF]?\s*(or below|or less)', outcome_name, re.IGNORECASE)
    if below_match:
        return (-999, int(below_match.group(1)))

    above_match = re.search(r'(\d+)\s*°?[fF]?\s*(or higher|or above|or more)', outcome_name, re.IGNORECASE)
    if above_match:
        return (int(above_match.group(1)), 999)

    range_match = re.search(r'(\d+)\s*[-–to]+\s*(\d+)', outcome_name)
    if range_match:
        low, high = int(range_match.group(1)), int(range_match.group(2))
        return (min(low, high), max(low, high))

    return None


# =============================================================================
# Simmer API - Core
# =============================================================================

def get_api_key():
    """Get Simmer API key from environment."""
    key = os.environ.get("SIMMER_API_KEY")
    if not key:
        print("Error: SIMMER_API_KEY environment variable not set")
        print("Get your API key from: simmer.markets/dashboard → SDK tab")
        sys.exit(1)
    return key


def sdk_request(api_key: str, method: str, endpoint: str, data: dict = None) -> dict:
    """Make authenticated request to Simmer SDK."""
    url = f"{SIMMER_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        if method == "GET":
            req = Request(url, headers=headers)
        else:
            body = json.dumps(data).encode() if data else None
            req = Request(url, data=body, headers=headers, method=method)

        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# Simmer API - Risk Monitoring
# =============================================================================

def set_risk_monitor(api_key: str, market_id: str, side: str, 
                     stop_loss_pct: float = 0.20, take_profit_pct: float = 0.50) -> dict:
    """
    Set stop-loss and take-profit for a position.
    The backend monitors every 15 min and auto-exits when thresholds hit.
    
    Args:
        market_id: Market ID
        side: 'yes' or 'no'
        stop_loss_pct: Exit if P&L drops below this (default 20% loss)
        take_profit_pct: Exit if P&L rises above this (default 50% gain)
    """
    result = sdk_request(api_key, "POST", f"/api/sdk/positions/{market_id}/monitor", {
        "side": side,
        "stop_loss_pct": stop_loss_pct,
        "take_profit_pct": take_profit_pct
    })
    if "error" in result:
        print(f"  ⚠️  Risk monitor failed: {result['error']}")
        return None
    return result


def get_risk_monitors(api_key: str) -> dict:
    """List all active risk monitors."""
    result = sdk_request(api_key, "GET", "/api/sdk/positions/monitors")
    if "error" in result:
        return None
    return result


def remove_risk_monitor(api_key: str, market_id: str, side: str) -> dict:
    """Remove risk monitor for a position."""
    result = sdk_request(api_key, "DELETE", f"/api/sdk/positions/{market_id}/monitor?side={side}")
    return result


# =============================================================================
# Simmer API - Portfolio & Context
# =============================================================================

def get_portfolio(api_key: str) -> dict:
    """
    Get portfolio summary from SDK.
    Returns: balance_usdc, total_exposure, positions_count, concentration
    """
    result = sdk_request(api_key, "GET", "/api/sdk/portfolio")
    if "error" in result:
        print(f"  ⚠️  Portfolio fetch failed: {result['error']}")
        return None
    return result


def get_market_context(api_key: str, market_id: str) -> dict:
    """
    Get market context with safeguards.
    Returns: market info, position, warnings, slippage, discipline
    """
    result = sdk_request(api_key, "GET", f"/api/sdk/context/{market_id}")
    if "error" in result:
        return None
    return result


def get_price_history(api_key: str, market_id: str) -> list:
    """
    Get price history for trend detection.
    Returns: list of {timestamp, price_yes, price_no}
    """
    result = sdk_request(api_key, "GET", f"/api/sdk/markets/{market_id}/history")
    if "error" in result:
        return []
    return result.get("points", [])


def check_context_safeguards(context: dict) -> tuple:
    """
    Check context for safeguards. Returns (should_trade, reasons).
    """
    if not context:
        return True, []  # No context = proceed (fail open)

    reasons = []
    market = context.get("market", {})
    warnings = context.get("warnings", [])
    discipline = context.get("discipline", {})
    slippage = context.get("slippage", {})

    # Check for deal-breakers in warnings
    for warning in warnings:
        if "MARKET RESOLVED" in str(warning).upper():
            return False, ["Market already resolved"]

    # Check flip-flop warning
    warning_level = discipline.get("warning_level", "none")
    if warning_level == "severe":
        return False, [f"Severe flip-flop warning: {discipline.get('flip_flop_warning', '')}"]
    elif warning_level == "mild":
        reasons.append("Mild flip-flop warning (proceed with caution)")

    # Check time to resolution
    time_str = market.get("time_to_resolution", "")
    if time_str:
        try:
            hours = 0
            if "d" in time_str:
                days = int(time_str.split("d")[0].strip())
                hours += days * 24
            if "h" in time_str:
                h_part = time_str.split("h")[0]
                if "d" in h_part:
                    h_part = h_part.split("d")[-1].strip()
                hours += int(h_part)

            if hours < TIME_TO_RESOLUTION_MIN_HOURS:
                return False, [f"Resolves in {hours}h - too soon"]
        except (ValueError, IndexError):
            pass

    # Check slippage
    estimates = slippage.get("estimates", []) if slippage else []
    if estimates:
        slippage_pct = estimates[0].get("slippage_pct", 0)
        if slippage_pct > SLIPPAGE_MAX_PCT:
            return False, [f"Slippage too high: {slippage_pct:.1%}"]

    return True, reasons


def detect_price_trend(history: list) -> dict:
    """
    Analyze price history for trends.
    Returns: {direction: "up"/"down"/"flat", change_24h: float, is_opportunity: bool}
    """
    if not history or len(history) < 2:
        return {"direction": "unknown", "change_24h": 0, "is_opportunity": False}

    # Get recent and older prices
    recent_price = history[-1].get("price_yes", 0.5)
    
    # Find price ~24h ago (assuming 15-min intervals, ~96 points)
    lookback = min(96, len(history) - 1)
    old_price = history[-lookback].get("price_yes", recent_price)

    if old_price == 0:
        return {"direction": "unknown", "change_24h": 0, "is_opportunity": False}

    change = (recent_price - old_price) / old_price

    if change < -PRICE_DROP_THRESHOLD:
        return {"direction": "down", "change_24h": change, "is_opportunity": True}
    elif change > PRICE_DROP_THRESHOLD:
        return {"direction": "up", "change_24h": change, "is_opportunity": False}
    else:
        return {"direction": "flat", "change_24h": change, "is_opportunity": False}


# =============================================================================
# Simmer API - Trading
# =============================================================================

def fetch_weather_markets():
    """Fetch weather-tagged markets from Simmer API."""
    url = f"{SIMMER_API_BASE}/api/markets?tags=weather&status=active&limit=100"
    data = fetch_json(url)

    if not data or "markets" not in data:
        print("  Failed to fetch markets from Simmer API")
        return []

    return data["markets"]


def execute_trade(api_key: str, market_id: str, side: str, amount: float) -> dict:
    """Execute a buy trade via Simmer SDK API with source tagging."""
    return sdk_request(api_key, "POST", "/api/sdk/trade", {
        "market_id": market_id,
        "side": side,
        "amount": amount,
        "venue": "polymarket",
        "source": TRADE_SOURCE,  # Track that this trade came from weather skill
    })


def execute_sell(api_key: str, market_id: str, shares: float) -> dict:
    """Execute a sell trade via Simmer SDK API with source tagging."""
    return sdk_request(api_key, "POST", "/api/sdk/trade", {
        "market_id": market_id,
        "side": "yes",
        "action": "sell",
        "shares": shares,
        "venue": "polymarket",
        "source": TRADE_SOURCE,
    })


def get_positions(api_key: str) -> list:
    """Get current positions from Simmer SDK API."""
    result = sdk_request(api_key, "GET", "/api/sdk/positions")
    if "error" in result:
        print(f"  Error fetching positions: {result['error']}")
        return []
    return result.get("positions", [])


def calculate_position_size(api_key: str, default_size: float, smart_sizing: bool) -> float:
    """
    Calculate position size based on portfolio or fall back to default.
    """
    if not smart_sizing:
        return default_size

    portfolio = get_portfolio(api_key)
    if not portfolio:
        print(f"  ⚠️  Smart sizing failed, using default ${default_size:.2f}")
        return default_size

    balance = portfolio.get("balance_usdc", 0)
    if balance <= 0:
        print(f"  ⚠️  No available balance, using default ${default_size:.2f}")
        return default_size

    smart_size = balance * SMART_SIZING_PCT
    # Cap at max position size
    smart_size = min(smart_size, MAX_POSITION_USD * 5)  # Allow up to 5x default for well-funded accounts
    # Floor at minimum viable trade
    smart_size = max(smart_size, 1.0)

    print(f"  💡 Smart sizing: ${smart_size:.2f} ({SMART_SIZING_PCT:.0%} of ${balance:.2f} balance)")
    return smart_size


# =============================================================================
# Exit Strategy
# =============================================================================

def check_exit_opportunities(api_key: str, dry_run: bool = False, use_safeguards: bool = True) -> tuple:
    """Check open positions for exit opportunities. Returns: (exits_found, exits_executed)"""
    positions = get_positions(api_key)

    if not positions:
        return 0, 0

    weather_positions = []
    for pos in positions:
        question = pos.get("question", "").lower()
        sources = pos.get("sources", [])
        # Check if from weather skill OR has weather keywords
        if TRADE_SOURCE in sources or any(kw in question for kw in ["temperature", "°f", "highest temp", "lowest temp"]):
            weather_positions.append(pos)

    if not weather_positions:
        return 0, 0

    print(f"\n📈 Checking {len(weather_positions)} weather positions for exit...")

    exits_found = 0
    exits_executed = 0

    for pos in weather_positions:
        market_id = pos.get("market_id")
        current_price = pos.get("current_price") or pos.get("price_yes") or 0
        shares = pos.get("shares_yes") or pos.get("shares") or 0
        question = pos.get("question", "Unknown")[:50]

        if shares < MIN_SHARES_PER_ORDER:
            continue

        if current_price >= EXIT_THRESHOLD:
            exits_found += 1
            print(f"  📤 {question}...")
            print(f"     Price ${current_price:.2f} >= exit threshold ${EXIT_THRESHOLD:.2f}")

            # Check safeguards before selling
            if use_safeguards:
                context = get_market_context(api_key, market_id)
                should_trade, reasons = check_context_safeguards(context)
                if not should_trade:
                    print(f"     ⏭️  Skipped: {'; '.join(reasons)}")
                    continue
                if reasons:
                    print(f"     ⚠️  Warnings: {'; '.join(reasons)}")

            if dry_run:
                print(f"     [DRY RUN] Would sell {shares:.1f} shares")
            else:
                print(f"     Selling {shares:.1f} shares...")
                result = execute_sell(api_key, market_id, shares)

                if result.get("success"):
                    exits_executed += 1
                    print(f"     ✅ Sold {shares:.1f} shares @ ${current_price:.2f}")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"     ❌ Sell failed: {error}")
        else:
            print(f"  📊 {question}...")
            print(f"     Price ${current_price:.2f} < exit threshold ${EXIT_THRESHOLD:.2f} - hold")

    return exits_found, exits_executed


# =============================================================================
# Main Strategy Logic
# =============================================================================

def run_weather_strategy(dry_run: bool = False, positions_only: bool = False, 
                         show_config: bool = False, smart_sizing: bool = False,
                         use_safeguards: bool = True, use_trends: bool = True):
    """Run the weather trading strategy."""
    print("🌤️  Simmer Weather Trading Skill")
    print("=" * 50)

    print(f"\n⚙️  Configuration:")
    print(f"  Entry threshold: {ENTRY_THRESHOLD:.0%} (buy below this)")
    print(f"  Exit threshold:  {EXIT_THRESHOLD:.0%} (sell above this)")
    print(f"  Max position:    ${MAX_POSITION_USD:.2f}")
    print(f"  Max trades/run:  {MAX_TRADES_PER_RUN}")
    print(f"  Locations:       {', '.join(ACTIVE_LOCATIONS)}")
    print(f"  Smart sizing:    {'✓ Enabled' if smart_sizing else '✗ Disabled'}")
    print(f"  Safeguards:      {'✓ Enabled' if use_safeguards else '✗ Disabled'}")
    print(f"  Trend detection: {'✓ Enabled' if use_trends else '✗ Disabled'}")

    if show_config:
        print("\n  To change settings, set environment variables:")
        print("    SIMMER_WEATHER_ENTRY=0.20")
        print("    SIMMER_WEATHER_EXIT=0.50")
        print("    SIMMER_WEATHER_MAX_POSITION=5.00")
        print("    SIMMER_WEATHER_MAX_TRADES=5")
        print("    SIMMER_WEATHER_LOCATIONS=NYC,Chicago,Miami")
        print("    SIMMER_WEATHER_SIZING_PCT=0.05  (for smart sizing)")
        return

    api_key = get_api_key()

    # Show portfolio if smart sizing enabled
    if smart_sizing:
        print("\n💰 Portfolio:")
        portfolio = get_portfolio(api_key)
        if portfolio:
            print(f"  Balance: ${portfolio.get('balance_usdc', 0):.2f}")
            print(f"  Exposure: ${portfolio.get('total_exposure', 0):.2f}")
            print(f"  Positions: {portfolio.get('positions_count', 0)}")
            by_source = portfolio.get('by_source', {})
            if by_source:
                print(f"  By source: {json.dumps(by_source, indent=4)}")

    if positions_only:
        print("\n📊 Current Positions:")
        positions = get_positions(api_key)
        if not positions:
            print("  No open positions")
        else:
            for pos in positions:
                print(f"  • {pos.get('question', 'Unknown')[:50]}...")
                sources = pos.get('sources', [])
                print(f"    YES: {pos.get('shares_yes', 0):.1f} | NO: {pos.get('shares_no', 0):.1f} | P&L: ${pos.get('pnl', 0):.2f} | Sources: {sources}")
        return

    print("\n📡 Fetching weather markets...")
    markets = fetch_weather_markets()
    print(f"  Found {len(markets)} weather markets")

    if not markets:
        print("  No weather markets available")
        return

    events = {}
    for market in markets:
        event_id = market.get("event_id") or market.get("event_name", "unknown")
        if event_id not in events:
            events[event_id] = []
        events[event_id].append(market)

    print(f"  Grouped into {len(events)} events")

    forecast_cache = {}
    trades_executed = 0
    opportunities_found = 0

    for event_id, event_markets in events.items():
        event_name = event_markets[0].get("event_name", "") if event_markets else ""
        event_info = parse_weather_event(event_name)

        if not event_info:
            continue

        location = event_info["location"]
        date_str = event_info["date"]
        metric = event_info["metric"]

        if location not in ACTIVE_LOCATIONS:
            continue

        print(f"\n📍 {location} {date_str} ({metric} temp)")

        if location not in forecast_cache:
            print(f"  Fetching NOAA forecast...")
            forecast_cache[location] = get_noaa_forecast(location)

        forecasts = forecast_cache[location]
        day_forecast = forecasts.get(date_str, {})
        forecast_temp = day_forecast.get(metric)

        if forecast_temp is None:
            print(f"  ⚠️  No forecast available for {date_str}")
            continue

        print(f"  NOAA forecast: {forecast_temp}°F")

        matching_market = None
        for market in event_markets:
            outcome_name = market.get("outcome_name", "")
            bucket = parse_temperature_bucket(outcome_name)

            if bucket and bucket[0] <= forecast_temp <= bucket[1]:
                matching_market = market
                break

        if not matching_market:
            print(f"  ⚠️  No bucket found for {forecast_temp}°F")
            continue

        outcome_name = matching_market.get("outcome_name", "")
        price = matching_market.get("external_price_yes") or 0.5
        market_id = matching_market.get("id")

        print(f"  Matching bucket: {outcome_name} @ ${price:.2f}")

        if price < MIN_TICK_SIZE:
            print(f"  ⏸️  Price ${price:.4f} below min tick ${MIN_TICK_SIZE} - skip (market at extreme)")
            continue
        if price > (1 - MIN_TICK_SIZE):
            print(f"  ⏸️  Price ${price:.4f} above max tradeable - skip (market at extreme)")
            continue

        # Check safeguards
        if use_safeguards:
            context = get_market_context(api_key, market_id)
            should_trade, reasons = check_context_safeguards(context)
            if not should_trade:
                print(f"  ⏭️  Safeguard blocked: {'; '.join(reasons)}")
                continue
            if reasons:
                print(f"  ⚠️  Warnings: {'; '.join(reasons)}")

        # Check price trend
        trend_bonus = ""
        if use_trends:
            history = get_price_history(api_key, market_id)
            trend = detect_price_trend(history)
            if trend["is_opportunity"]:
                trend_bonus = f" 📉 (dropped {abs(trend['change_24h']):.0%} in 24h - stronger signal!)"
            elif trend["direction"] == "up":
                trend_bonus = f" 📈 (up {trend['change_24h']:.0%} in 24h)"

        if price < ENTRY_THRESHOLD:
            position_size = calculate_position_size(api_key, MAX_POSITION_USD, smart_sizing)

            min_cost_for_shares = MIN_SHARES_PER_ORDER * price
            if min_cost_for_shares > position_size:
                print(f"  ⚠️  Position size ${position_size:.2f} too small for {MIN_SHARES_PER_ORDER} shares at ${price:.2f}")
                continue

            opportunities_found += 1
            print(f"  ✅ Below threshold (${ENTRY_THRESHOLD:.2f}) - BUY opportunity!{trend_bonus}")

            # Check rate limit
            if trades_executed >= MAX_TRADES_PER_RUN:
                print(f"  ⏸️  Max trades per run ({MAX_TRADES_PER_RUN}) reached - skipping")
                continue

            if dry_run:
                print(f"  [DRY RUN] Would buy ${position_size:.2f} worth (~{position_size/price:.1f} shares)")
            else:
                print(f"  Executing trade...")
                result = execute_trade(api_key, market_id, "yes", position_size)

                if result.get("success"):
                    trades_executed += 1
                    shares = result.get("shares_bought") or result.get("shares") or 0
                    print(f"  ✅ Bought {shares:.1f} shares @ ${price:.2f}")
                    
                    # Set up risk monitor (stop-loss 25%, take-profit 60%)
                    risk_result = set_risk_monitor(api_key, market_id, "yes", 
                                                   stop_loss_pct=0.25, take_profit_pct=0.60)
                    if risk_result and risk_result.get("success"):
                        print(f"  🛡️  Risk monitor set: SL -25% / TP +60%")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"  ❌ Trade failed: {error}")
        else:
            print(f"  ⏸️  Price ${price:.2f} above threshold ${ENTRY_THRESHOLD:.2f} - skip")

    exits_found, exits_executed = check_exit_opportunities(api_key, dry_run, use_safeguards)

    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"  Events scanned: {len(events)}")
    print(f"  Entry opportunities: {opportunities_found}")
    print(f"  Exit opportunities:  {exits_found}")
    print(f"  Trades executed:     {trades_executed + exits_executed}")

    if dry_run:
        print("\n  [DRY RUN MODE - no real trades executed]")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simmer Weather Trading Skill")
    parser.add_argument("--dry-run", action="store_true", help="Show opportunities without trading")
    parser.add_argument("--positions", action="store_true", help="Show current positions only")
    parser.add_argument("--config", action="store_true", help="Show current config")
    parser.add_argument("--smart-sizing", action="store_true", help="Use portfolio-based position sizing")
    parser.add_argument("--no-safeguards", action="store_true", help="Disable context safeguards")
    parser.add_argument("--no-trends", action="store_true", help="Disable price trend detection")
    args = parser.parse_args()

    run_weather_strategy(
        dry_run=args.dry_run, 
        positions_only=args.positions, 
        show_config=args.config,
        smart_sizing=args.smart_sizing,
        use_safeguards=not args.no_safeguards,
        use_trends=not args.no_trends,
    )
