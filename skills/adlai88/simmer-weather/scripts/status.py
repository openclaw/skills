#!/usr/bin/env python3
"""
Simmer Account Status

Shows wallet balance, positions, and recent activity.

Usage:
    python scripts/status.py
    python scripts/status.py --positions  # Detailed position list
"""

import os
import sys
import json
import argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SIMMER_API_BASE = "https://api.simmer.markets"

def api_request(api_key: str, endpoint: str) -> dict:
    """Make authenticated request to Simmer API."""
    url = f"{SIMMER_API_BASE}{endpoint}"
    req = Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"❌ API Error {e.code}: {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"❌ Connection error: {e.reason}")
        sys.exit(1)

def format_usd(amount: float) -> str:
    """Format as USD."""
    return f"${amount:,.2f}"

def main():
    parser = argparse.ArgumentParser(description="Check Simmer account status")
    parser.add_argument("--positions", action="store_true", help="Show detailed positions")
    args = parser.parse_args()

    api_key = os.environ.get("SIMMER_API_KEY")
    if not api_key:
        print("❌ SIMMER_API_KEY environment variable not set")
        print("   Get your API key from: https://simmer.markets/dashboard")
        sys.exit(1)

    # Get portfolio summary
    print("📊 Fetching account status...\n")
    portfolio = api_request(api_key, "/api/sdk/portfolio")

    balance = portfolio.get("balance_usdc", 0)
    exposure = portfolio.get("total_exposure", 0)
    positions_count = portfolio.get("positions_count", 0)
    pnl_total = portfolio.get("pnl_total")
    pnl_24h = portfolio.get("pnl_24h")

    # Display summary
    print("=" * 50)
    print("💰 ACCOUNT SUMMARY")
    print("=" * 50)
    print(f"  Available Balance:  {format_usd(balance)}")
    print(f"  Total Exposure:     {format_usd(exposure)}")
    print(f"  Open Positions:     {positions_count}")
    
    if pnl_total is not None:
        pnl_emoji = "📈" if pnl_total >= 0 else "📉"
        print(f"  Total PnL:          {pnl_emoji} {format_usd(pnl_total)}")
    
    if pnl_24h is not None:
        pnl_24h_emoji = "📈" if pnl_24h >= 0 else "📉"
        print(f"  24h PnL:            {pnl_24h_emoji} {format_usd(pnl_24h)}")
    
    # Concentration warning
    concentration = portfolio.get("concentration", {})
    top_market_pct = concentration.get("top_market_pct", 0)
    if top_market_pct > 0.5:
        print(f"\n  ⚠️  High concentration: {top_market_pct:.0%} in top market")

    # By source breakdown
    by_source = portfolio.get("by_source", {})
    if by_source:
        print("\n  📁 By Source:")
        for source, data in by_source.items():
            src_positions = data.get("positions", 0)
            src_exposure = data.get("exposure", 0)
            print(f"      {source}: {src_positions} positions, {format_usd(src_exposure)}")

    print("=" * 50)

    # Detailed positions if requested
    if args.positions:
        print("\n📋 OPEN POSITIONS")
        print("=" * 50)
        result = api_request(api_key, "/api/sdk/positions")
        positions = result.get("positions", []) if isinstance(result, dict) else result
        
        if not positions:
            print("  No open positions")
        else:
            for pos in positions:
                question = pos.get("question", pos.get("market_id", "Unknown"))
                # Truncate long questions
                if len(question) > 50:
                    question = question[:47] + "..."
                
                shares_yes = pos.get("shares_yes", 0)
                shares_no = pos.get("shares_no", 0)
                current_price = pos.get("current_price", 0)
                cost_basis = pos.get("cost_basis", 0)
                pnl = pos.get("pnl", 0)
                
                # Determine position side
                if shares_yes > 0:
                    side = "YES"
                    shares = shares_yes
                elif shares_no > 0:
                    side = "NO"
                    shares = shares_no
                else:
                    continue  # Skip empty positions
                
                pnl_indicator = "🟢" if pnl >= 0 else "🔴"
                print(f"\n  {question}")
                print(f"    {side}: {shares:.2f} shares, cost ${cost_basis:.2f}")
                print(f"    Current: {current_price:.1%} | {pnl_indicator} PnL: {format_usd(pnl)}")
        
        print("\n" + "=" * 50)

    # Helpful tips
    if balance == 0:
        print("\n💡 Tip: Deposit funds at https://simmer.markets/dashboard")
    
    print()

if __name__ == "__main__":
    main()
