#!/usr/bin/env python3
"""
Kraken Portfolio CLI - Smart Wrapper for Clawdbot

High-level commands with accurate portfolio calculations.
For raw API access, use kraken_api.py directly.

Usage:
    python kraken_cli.py <command> [--options]

Commands:
    # Portfolio (Smart Calculations)
    summary              - Complete portfolio overview (no double-counting)
    net-worth            - Total net worth calculation
    performance          - Returns vs deposits
    holdings             - Asset breakdown with current prices
    staking              - Staking positions and rewards

    # Pass-through to kraken_api.py
    api <command> [args] - Run any kraken_api.py command directly
"""

import os
import sys
import argparse
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Import the API layer
from kraken_api import (
    get_clients,
    format_currency,
    cmd_balance,
    cmd_portfolio,
    cmd_earn,
    cmd_ticker,
    cmd_ledger,
)

from dotenv import load_dotenv
from kraken.spot import User, Market, Earn, Funding

# Load .env file from skill directory
skill_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(skill_dir, ".env"))


def get_asset_prices(market: Market, pairs: list[str]) -> dict[str, float]:
    """Fetch current USD prices for a list of asset pairs."""
    prices = {}
    for pair in pairs:
        try:
            result = market.get_ticker(pair=pair)
            if result and pair in result:
                prices[pair] = float(result[pair].get("c", [0])[0])
        except Exception:
            pass
    return prices


def calculate_portfolio_summary(
    user: Optional[User],
    market: Market,
    earn: Optional[Earn],
) -> dict:
    """
    Calculate accurate portfolio summary without double-counting.

    Returns dict with:
    - main_equity: USD value of Main wallet (includes Auto Earn)
    - earn_wallet: USD value of Earn wallet (bonded/locked rewards)
    - total_net_worth: main_equity + earn_wallet
    - spot_balances: dict of asset -> quantity
    - staking_allocations: list of staking positions
    - total_staking_rewards: sum of all rewards earned
    """
    result = {
        "main_equity": 0.0,
        "earn_wallet": 0.0,
        "total_net_worth": 0.0,
        "free_margin": 0.0,
        "spot_balances": {},
        "staking_allocations": [],
        "total_staking_rewards": 0.0,
        "error": None,
    }

    if not user:
        result["error"] = "API credentials required"
        return result

    # Step 1: Get Trade Balance (Equity = Main wallet value)
    try:
        trade_balance = user.get_trade_balance(asset="USD")
        if trade_balance:
            result["main_equity"] = float(trade_balance.get("eb", 0))
            result["free_margin"] = float(trade_balance.get("mf", 0))
    except Exception as e:
        result["error"] = f"Trade balance error: {e}"
        return result

    # Step 2: Get Spot Balances (for breakdown)
    try:
        balances = user.get_account_balance()
        if balances:
            for asset, qty in balances.items():
                if float(qty) > 0:
                    result["spot_balances"][asset] = float(qty)
    except Exception:
        pass  # Non-critical

    # Step 3: Get Earn Allocations and classify by lock type
    # Kraken has two staking types:
    # - 'flex' (Auto Earn): Assets stay in Main wallet, included in Trade Balance
    # - 'bonded': Assets move to Earn wallet, NOT in Trade Balance
    if earn:
        try:
            # First get strategies to build lock_type map
            strategies = earn.list_earn_strategies()
            lock_types = {}
            for strat in strategies.get("items", []):
                lock_types[strat.get("id")] = strat.get("lock_type", {}).get("type", "unknown")

            # Now get allocations and classify
            earn_data = earn.list_earn_allocations(
                converted_asset="USD",
                hide_zero_allocations="true"
            )
            if earn_data:
                result["total_staking_rewards"] = float(earn_data.get("total_rewarded", 0))

                bonded_value = 0.0
                flex_value = 0.0

                for item in earn_data.get("items", []):
                    strat_id = item.get("strategy_id", "")
                    lock_type = lock_types.get(strat_id, "unknown")
                    is_bonded = lock_type == "bonded"

                    usd_value = float(item.get("amount_allocated", {}).get("total", {}).get("converted", 0))
                    rewards = float(item.get("total_rewarded", {}).get("converted", 0))

                    allocation = {
                        "asset": item.get("native_asset", "?"),
                        "amount": float(item.get("amount_allocated", {}).get("total", {}).get("native", 0)),
                        "usd_value": usd_value,
                        "rewards": rewards,
                        "lock_type": lock_type,
                        "is_bonded": is_bonded,
                    }
                    result["staking_allocations"].append(allocation)

                    if is_bonded:
                        bonded_value += usd_value
                    else:
                        flex_value += usd_value

                # Earn wallet = bonded staking (NOT in main equity)
                result["earn_wallet"] = bonded_value
                result["flex_value"] = flex_value

        except Exception:
            pass  # Non-critical

    # Step 4: Calculate Total (Main + Earn rewards)
    # Note: Earn wallet on dashboard shows accrued rewards not yet in Main
    result["total_net_worth"] = result["main_equity"] + result["earn_wallet"]

    return result


def cmd_summary() -> str:
    """Generate complete portfolio summary with accurate calculations."""
    user, market, earn, _ = get_clients()

    summary = calculate_portfolio_summary(user, market, earn)

    if summary["error"]:
        return f"Error: {summary['error']}"

    lines = []
    lines.append("=" * 50)
    lines.append("           KRAKEN PORTFOLIO SUMMARY")
    lines.append("=" * 50)
    lines.append("")

    # Total Net Worth
    lines.append("TOTAL NET WORTH")
    lines.append(f"  Main Wallet (Equity):    ${summary['main_equity']:,.2f}")
    lines.append(f"  Earn Wallet (Bonded):    ${summary['earn_wallet']:,.2f}")
    lines.append(f"  ─────────────────────────────────")
    lines.append(f"  TOTAL:                   ${summary['total_net_worth']:,.2f}")
    lines.append("")

    # Staking Positions - separate by type
    if summary["staking_allocations"]:
        bonded = [a for a in summary["staking_allocations"] if a.get("is_bonded")]
        flex = [a for a in summary["staking_allocations"] if not a.get("is_bonded")]

        if flex:
            lines.append("AUTO EARN (Flexible) - in Main Wallet")
            for alloc in sorted(flex, key=lambda x: x["usd_value"], reverse=True):
                if alloc["usd_value"] > 0.01:
                    lines.append(f"  {alloc['asset']:6s}: ${alloc['usd_value']:>10,.2f} "
                                f"(rewards: ${alloc['rewards']:,.2f})")
            lines.append("")

        if bonded:
            lines.append("BONDED STAKING - in Earn Wallet")
            for alloc in sorted(bonded, key=lambda x: x["usd_value"], reverse=True):
                if alloc["usd_value"] > 0.01:
                    lines.append(f"  {alloc['asset']:6s}: ${alloc['usd_value']:>10,.2f} "
                                f"(rewards: ${alloc['rewards']:,.2f})")
            lines.append("")

        lines.append(f"  Total Staking Rewards:   ${summary['total_staking_rewards']:,.2f}")
        lines.append("")

    # Spot Holdings
    if summary["spot_balances"]:
        lines.append("ASSET HOLDINGS")
        for asset, qty in sorted(summary["spot_balances"].items(), key=lambda x: x[1], reverse=True):
            # Mark staked assets
            is_staked = any(a["asset"] == asset.replace(".S", "") for a in summary["staking_allocations"])
            staked_marker = " (staked)" if ".S" in asset or is_staked else ""
            lines.append(f"  {asset:8s}: {qty:>12.6f}{staked_marker}")
        lines.append("")

    lines.append("=" * 50)
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)

    return "\n".join(lines)


def cmd_net_worth() -> str:
    """Get just the net worth calculation."""
    user, market, earn, _ = get_clients()

    summary = calculate_portfolio_summary(user, market, earn)

    if summary["error"]:
        return f"Error: {summary['error']}"

    lines = [
        "=== NET WORTH ===",
        f"  Main Wallet:   ${summary['main_equity']:,.2f}",
        f"  Earn Wallet:   ${summary['earn_wallet']:,.2f}",
        f"  TOTAL:         ${summary['total_net_worth']:,.2f}",
    ]
    return "\n".join(lines)


def cmd_performance() -> str:
    """Calculate performance vs deposits."""
    user, market, earn, _ = get_clients()

    if not user:
        return "Error: API credentials required"

    # Get current portfolio value
    summary = calculate_portfolio_summary(user, market, earn)
    if summary["error"]:
        return f"Error: {summary['error']}"

    # Get deposit history from ledger
    total_deposits = 0.0
    total_withdrawals = 0.0

    try:
        ledger_result = user.get_ledgers_info()
        if ledger_result and "ledger" in ledger_result:
            for _, entry in ledger_result.get("ledger", {}).items():
                entry_type = entry.get("type", "")
                asset = entry.get("asset", "")
                amount = float(entry.get("amount", 0))

                # Only count fiat deposits/withdrawals
                if asset in ["ZUSD", "USD", "EUR", "ZEUR", "GBP"]:
                    if entry_type == "deposit":
                        total_deposits += abs(amount)
                    elif entry_type == "withdrawal":
                        total_withdrawals += abs(amount)
    except Exception as e:
        return f"Error reading ledger: {e}"

    net_investment = total_deposits - total_withdrawals
    current_value = summary["total_net_worth"]
    total_return = current_value - net_investment
    return_pct = (total_return / net_investment * 100) if net_investment > 0 else 0

    lines = [
        "=== PERFORMANCE ===",
        f"  Total Deposits:     ${total_deposits:,.2f}",
        f"  Total Withdrawals:  ${total_withdrawals:,.2f}",
        f"  Net Investment:     ${net_investment:,.2f}",
        "",
        f"  Current Value:      ${current_value:,.2f}",
        f"  Total Return:       ${total_return:+,.2f} ({return_pct:+.1f}%)",
        "",
        f"  Staking Rewards:    ${summary['total_staking_rewards']:,.2f}",
    ]
    return "\n".join(lines)


def cmd_holdings() -> str:
    """Show asset holdings with current USD values."""
    user, market, earn, _ = get_clients()

    if not user:
        return "Error: API credentials required"

    try:
        balances = user.get_account_balance()
        if not balances:
            return "No balance data."

        # Asset pair mapping for price lookups
        pair_map = {
            "XXBT": "XXBTZUSD",
            "XETH": "XETHZUSD",
            "SOL": "SOLUSD",
            "DOT": "DOTUSD",
            "SOL.S": "SOLUSD",
            "DOT.S": "DOTUSD",
            "SOL03.S": "SOLUSD",
            "DOT28.S": "DOTUSD",
        }

        lines = ["=== ASSET HOLDINGS ==="]
        lines.append(f"  {'Asset':<10} {'Quantity':>14} {'Price':>12} {'Value':>12}")
        lines.append("  " + "-" * 50)

        total_usd = 0.0

        for asset, qty in sorted(balances.items(), key=lambda x: float(x[1]), reverse=True):
            qty_float = float(qty)
            if qty_float <= 0:
                continue

            # Get price
            pair = pair_map.get(asset, f"{asset}USD")
            price = 0.0
            try:
                result = market.get_ticker(pair=pair)
                if result and pair in result:
                    price = float(result[pair].get("c", [0])[0])
            except Exception:
                pass

            value = qty_float * price
            total_usd += value

            price_str = f"${price:,.2f}" if price > 0 else "N/A"
            value_str = f"${value:,.2f}" if price > 0 else "N/A"

            lines.append(f"  {asset:<10} {qty_float:>14.6f} {price_str:>12} {value_str:>12}")

        lines.append("  " + "-" * 50)
        lines.append(f"  {'TOTAL':<10} {'':<14} {'':<12} ${total_usd:>11,.2f}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_staking() -> str:
    """Show staking positions and rewards."""
    user, market, earn, _ = get_clients()

    if not earn:
        return "Error: API credentials required"

    try:
        result = earn.list_earn_allocations(
            converted_asset="USD",
            hide_zero_allocations="true"
        )
        if not result or "items" not in result:
            return "No staking positions found."

        total_allocated = float(result.get("total_allocated", 0))
        total_rewarded = float(result.get("total_rewarded", 0))

        lines = ["=== STAKING POSITIONS ==="]
        lines.append(f"  Total Allocated: ${total_allocated:,.2f}")
        lines.append(f"  Total Rewards:   ${total_rewarded:,.2f}")
        lines.append("")

        for item in result.get("items", []):
            asset = item.get("native_asset", "?")
            amount = item.get("amount_allocated", {}).get("total", {}).get("native", "0")
            usd_value = float(item.get("amount_allocated", {}).get("total", {}).get("converted", 0))
            rewards = float(item.get("total_rewarded", {}).get("converted", 0))

            lines.append(f"  {asset}")
            lines.append(f"    Amount:  {amount}")
            lines.append(f"    Value:   ${usd_value:,.2f}")
            lines.append(f"    Rewards: ${rewards:,.2f}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_api_passthrough(args: list[str]) -> str:
    """Pass through to kraken_api.py for raw commands."""
    import subprocess
    api_script = os.path.join(skill_dir, "kraken_api.py")
    result = subprocess.run(
        ["python", api_script] + args,
        capture_output=True,
        text=True,
        cwd=skill_dir,
    )
    output = result.stdout + result.stderr
    return output.strip()


def main():
    # Handle high-level commands first
    high_level_cmds = {"summary", "net-worth", "performance", "holdings", "staking", "help", "-h", "--help"}

    if len(sys.argv) < 2:
        # Default to summary
        print(cmd_summary())
        return

    cmd = sys.argv[1].lower()

    # High-level commands with smart calculations
    if cmd == "summary":
        print(cmd_summary())
    elif cmd == "net-worth":
        print(cmd_net_worth())
    elif cmd == "performance":
        print(cmd_performance())
    elif cmd == "holdings":
        print(cmd_holdings())
    elif cmd == "staking":
        print(cmd_staking())
    elif cmd in ("help", "-h", "--help"):
        print(__doc__)
        print("\nFor raw API commands, pass them directly:")
        print("  python kraken_cli.py ticker --pair XXBTZUSD")
        print("  python kraken_cli.py balance")
        print("  python kraken_cli.py api <command> [args]  # explicit API call")

    # Pass-through to kraken_api.py for all other commands
    elif cmd == "api":
        # Explicit API passthrough
        print(run_api_passthrough(sys.argv[2:]))
    else:
        # Direct passthrough for backward compatibility
        print(run_api_passthrough(sys.argv[1:]))


if __name__ == "__main__":
    main()
