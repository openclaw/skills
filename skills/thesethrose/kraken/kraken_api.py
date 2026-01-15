#!/usr/bin/env python3
"""
Kraken Crypto CLI Tool for Clawdbot
A command-line interface for managing your Kraken account.

Usage:
    python kraken_cli.py <command> [--options]

Commands:
    # Account Data (Private)
    balance              - Get all account balances
    balance-ex           - Get extended balance (includes reserved funds)
    portfolio            - Get trade balance summary (equity, PnL, cost basis)
    open-orders          - Get open orders
    closed-orders        - Get closed orders
    orders <refid>       - Query specific order by ID
    trades               - Get trade history
    query-trades <refid> - Query specific trade by ID
    open-positions       - Get open positions
    ledger               - Get ledger entries (all types)
    ledger --asset BTC   - Filter ledger by asset
    query-ledger <refid> - Query specific ledger entry
    volume               - Get trade volume (30-day)

    # Market Data (Public)
    ticker <pair>        - Get ticker info (price, 24h vol, high/low)
    assets               - Get asset info (altnames, decimals)
    pairs                - Get tradable asset pairs
    ohlc <pair> [interval] - Get OHLC data (default: 1440min)
    depth <pair> [count]  - Get order book (default: 100 bids/asks)
    recent-trades <pair> - Get recent trades
    spreads <pair>       - Get recent spreads
    status               - Get system status
    time                 - Get server time

    # Staking (Private)
    earn                 - Show stakeable assets info
    earn-positions       - Show current staking allocations
    earn-status          - Pending stake requests
    earn-dealloc-status  - Pending unstake requests
    earn-strategies      - Available yield programs

    # Deposits (Private)
    deposits-methods     - Show available deposit methods
    deposits-address     - Get deposit address for an asset (--asset required)
"""

import os
import sys
import argparse
from datetime import datetime
from decimal import Decimal
from typing import Optional

from dotenv import load_dotenv
from kraken.spot import User, Market, Earn, Funding

# Load .env file from skill directory
skill_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(skill_dir, ".env"))


def get_clients() -> tuple[User | None, Market, Earn | None, Funding | None]:
    """Initialize and return Kraken clients."""
    api_key = os.environ.get("KRAKEN_API_KEY")
    api_secret = os.environ.get("KRAKEN_API_SECRET")

    has_creds = api_key and api_secret

    return (
        User(key=api_key or "", secret=api_secret or "") if has_creds else None,
        Market(),
        Earn(key=api_key or "", secret=api_secret or "") if has_creds else None,
        Funding(key=api_key or "", secret=api_secret or "") if has_creds else None,
    )


def format_currency(amount: str, decimals: int = 4) -> str:
    """Format decimal amount nicely."""
    try:
        return f"{Decimal(amount):.{decimals}f}"
    except:
        return amount


# ============ ACCOUNT DATA (PRIVATE) ============

def cmd_balance(user: Optional[User]) -> str:
    """Get account balances."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_account_balance()
        if not result or isinstance(result, list):
            return "No balances found."

        lines = ["=== Account Balances ==="]
        for asset, balance in sorted(result.items(), key=lambda x: float(x[1]), reverse=True):
            if float(balance) > 0:
                lines.append(f"  {asset:8s}: {format_currency(balance, 6)}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_balance_ex(user: Optional[User]) -> str:
    """Get extended balance including reserved funds."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_account_balance()
        if not result:
            return "No balance data."

        lines = ["=== Extended Balances ==="]
        lines.append("(Including funds reserved in open orders)")
        lines.append("")
        for asset, balance in sorted(result.items(), key=lambda x: float(x[1]), reverse=True):
            if float(balance) > 0:
                lines.append(f"  {asset:8s}: {format_currency(balance, 6)}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_portfolio(user: Optional[User]) -> str:
    """Get extended portfolio with trade balances."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_trade_balance(asset="USD")
        if not result:
            return "No trade balance data."

        lines = ["=== Trade Balance (USD) ==="]
        lines.append(f"  Equity:          ${format_currency(result.get('eb', '0'))}")
        lines.append(f"  Free:            ${format_currency(result.get('tb', '0'))}")
        lines.append(f"  Free Margin:     ${format_currency(result.get('mf', '0'))}")
        lines.append(f"  Unrealized PnL:  ${format_currency(result.get('up', '0'))}")
        lines.append(f"  Cost Basis:      ${format_currency(result.get('bc', '0'))}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_open_orders(user: Optional[User]) -> str:
    """Get open orders."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_open_orders()
        if not result or "open" not in result or not result.get("open"):
            return "No open orders."

        lines = ["=== Open Orders ==="]
        for refid, order in result.get("open", {}).items():
            timestamp = datetime.fromtimestamp(float(order.get("opentm", 0)))
            side = "BUY" if order.get("descr", {}).get("type") == "buy" else "SELL"
            pair = order.get("descr", {}).get("pair", "?")
            price = order.get("descr", {}).get("price", "?")
            vol = order.get("vol", "?")
            lines.append(f"  [{side:4s}] {timestamp.strftime('%Y-%m-%d %H:%M')} {pair:10s} {vol:>12s} @ {price}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_closed_orders(user: Optional[User], limit: int = 20) -> str:
    """Get closed orders."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_closed_orders()
        if not result or "closed" not in result or not result.get("closed"):
            return "No closed orders."

        orders = list(result.get("closed", {}).items())[:limit]
        lines = ["=== Closed Orders ==="]
        for refid, order in orders:
            timestamp = datetime.fromtimestamp(float(order.get("closetm", 0)))
            side = "BUY" if order.get("descr", {}).get("type") == "buy" else "SELL"
            pair = order.get("descr", {}).get("pair", "?")
            vol = order.get("vol", "?")
            status = order.get("status", "?")
            lines.append(f"  [{side:4s}] {timestamp.strftime('%Y-%m-%d %H:%M')} {pair:10s} {vol:>12s} [{status}]")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_query_orders(user: Optional[User], refid: Optional[str] = None) -> str:
    """Query specific orders by ID."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        if refid:
            result = user.get_orders_info(txid=refid)
            if not result:
                return f"Order {refid} not found."
            orders = {"": result} if "txid" in result else result
        else:
            result = user.get_open_orders()
            orders = result.get("open", {})

        lines = ["=== Order Details ==="]
        for rid, order in orders.items():
            descr = order.get("descr", {})
            lines.append(f"  ID: {rid}")
            lines.append(f"  Pair: {descr.get('pair', '?')}")
            lines.append(f"  Type: {descr.get('type', '?')} {descr.get('ordertype', '?')}")
            lines.append(f"  Price: {descr.get('price', '?')}")
            lines.append(f"  Volume: {order.get('vol', '?')}")
            lines.append(f"  Status: {order.get('status', '?')}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_trades(user: Optional[User], limit: int = 20) -> str:
    """Get trade history."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_trades_history()
        if not result or "trades" not in result or not result.get("trades"):
            return "No trades found."

        trades = result.get("trades", {})
        sorted_trades = sorted(trades.items(), key=lambda x: float(x[1].get("time", 0)), reverse=True)
        lines = ["=== Trade History ==="]
        for refid, trade in sorted_trades[:limit]:
            timestamp = datetime.fromtimestamp(float(trade.get("time", 0)))
            side = "BUY" if trade.get("type") == "buy" else "SELL"
            lines.append(f"  [{side:4s}] {timestamp.strftime('%Y-%m-%d %H:%M')} "
                        f"{trade.get('pair', '?'):10s} {trade.get('vol', '?'):>12s} "
                        f"@ ${trade.get('price', '?')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_query_trades(user: Optional[User], refid: Optional[str] = None) -> str:
    """Query specific trades by ID."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        if refid:
            result = user.get_trades_info(txid=refid)
            if not result:
                return f"Trade {refid} not found."
            trades = {"": result} if "txid" in result else result
        else:
            result = user.get_trades_history()
            trades = result.get("trades", {})

        lines = ["=== Trade Details ==="]
        for rid, trade in list(trades.items())[:10]:
            timestamp = datetime.fromtimestamp(float(trade.get("time", 0)))
            side = "BUY" if trade.get("type") == "buy" else "SELL"
            lines.append(f"  ID: {rid}")
            lines.append(f"  [{side:4s}] {timestamp.strftime('%Y-%m-%d %H:%M')} {trade.get('pair', '?')}")
            lines.append(f"  Volume: {trade.get('vol', '?')} @ ${trade.get('price', '?')}")
            lines.append(f"  Fee: {trade.get('fee', '?')} {trade.get('fee_currency', '')}")
            lines.append(f"  Cost: {trade.get('cost', '?')}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_open_positions(user: Optional[User]) -> str:
    """Get open positions."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_open_positions()
        if not result or not result:
            return "No open positions."

        lines = ["=== Open Positions ==="]
        for refid, pos in result.items():
            pair = pos.get("pair", "?")
            vol = pos.get("vol", "?")
            margin = pos.get("margin", "?")
            pnl = pos.get("net", "?")
            lines.append(f"  {pair:10s}: {vol:>10s} (margin: {margin}, pnl: {pnl})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_ledger(user: Optional[User], asset: Optional[str] = None, limit: int = 20) -> str:
    """Get ledger entries."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_ledgers_info(asset=asset) if asset else user.get_ledgers_info()
        if not result or "ledger" not in result or not result.get("ledger"):
            return "No ledger entries found."

        ledger = result.get("ledger", {})
        entries = sorted(ledger.items(), key=lambda x: int(x[0], 36), reverse=True)[:limit]
        lines = [f"=== Ledger Entries{' (' + asset + ')' if asset else ''} ==="]
        for refid, entry in entries:
            timestamp = datetime.fromtimestamp(float(entry.get("time", 0)))
            lines.append(f"  [{entry.get('type', '?').upper():10s}] {timestamp.strftime('%Y-%m-%d %H:%M')} "
                        f"{entry.get('asset', '?'):6s} {entry.get('amount', '?'):>15s} "
                        f"(fee: {entry.get('fee', '?')})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_query_ledger(user: Optional[User], refid: Optional[str] = None) -> str:
    """Query specific ledger entry."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        if not refid:
            return "Error: --refid required for query-ledger"

        result = user.get_ledgers_info()
        if not result or "ledger" not in result:
            return "No ledger data."

        # Search for the specific refid
        ledger = result.get("ledger", {})
        for rid, entry in ledger.items():
            if rid == refid:
                timestamp = datetime.fromtimestamp(float(entry.get("time", 0)))
                lines = ["=== Ledger Entry Details ==="]
                lines.append(f"  ID: {rid}")
                lines.append(f"  Type: {entry.get('type', '?')}")
                lines.append(f"  Subtype: {entry.get('subtype', '?')}")
                lines.append(f"  Asset: {entry.get('asset', '?')}")
                lines.append(f"  Amount: {entry.get('amount', '?')}")
                lines.append(f"  Fee: {entry.get('fee', '?')}")
                lines.append(f"  Balance: {entry.get('balance', '?')}")
                lines.append(f"  Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                return "\n".join(lines)

        return f"Ledger entry {refid} not found."
    except Exception as e:
        return f"Error: {e}"


def cmd_volume(user: Optional[User]) -> str:
    """Get trade volume (30-day)."""
    if not user:
        return "Error: API credentials required for this command."
    try:
        result = user.get_trade_volume()
        if not result:
            return "No volume data."

        lines = ["=== Trade Volume (30-day) ==="]
        if "volume" in result:
            lines.append(f"  Total Volume: {result['volume']}")
        if "fees" in result:
            lines.append("  Fees:")
            for pair, data in result["fees"].items():
                lines.append(f"    {pair}: {data.get('fee', '?')}%")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


# ============ MARKET DATA (PUBLIC) ============

def cmd_ticker(market: Market, pair: str) -> str:
    """Get ticker price."""
    try:
        result = market.get_ticker(pair=pair)
        if not result:
            return f"No ticker data for {pair}."

        ticker = result.get(pair, result)
        lines = [f"=== Ticker {pair} ==="]
        lines.append(f"  Price:      ${ticker.get('c', ['?'])[0]}")
        lines.append(f"  24h Volume: {ticker.get('v', ['?'])[0]}")
        lines.append(f"  High:       ${ticker.get('h', ['?'])[0]}")
        lines.append(f"  Low:        ${ticker.get('l', ['?'])[0]}")
        lines.append(f"  24h Change: {ticker.get('p', ['?'])[0]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_assets(market: Market) -> str:
    """Get asset info."""
    try:
        result = market.get_assets()
        if not result:
            return "No asset data."

        lines = ["=== Assets ==="]
        for asset, data in result.items():
            altname = data.get("altname", asset)
            decimals = data.get("decimals", "?")
            display_decimals = data.get("display_decimals", "?")
            lines.append(f"  {asset:8s}: {altname} (decimals: {decimals}/{display_decimals})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_asset_pairs(market: Market) -> str:
    """Get tradable asset pairs."""
    try:
        result = market.get_asset_pairs()
        if not result:
            return "No pairs data."

        lines = ["=== Asset Pairs ==="]
        for pair, data in result.items():
            wsname = data.get("wsname", pair)
            base = data.get("base", "?")
            quote = data.get("quote", "?")
            lines.append(f"  {pair:12s}: {wsname} ({base}/{quote})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_ohlc(market: Market, pair: str, interval: int = 1440) -> str:
    """Get OHLC data."""
    try:
        result = market.get_ohlc(pair=pair, interval=interval)
        if not result or pair not in result:
            return f"No OHLC data for {pair}."

        # Data is a list of candles under the pair key: [time, open, high, low, close, vwap, volume, count]
        ohlc_data = result.get(pair, [])
        lines = [f"=== OHLC {pair} (interval: {interval}) ==="]
        for candle in ohlc_data[:10]:
            timestamp = datetime.fromtimestamp(float(candle[0]))
            lines.append(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} O:{candle[1]} H:{candle[2]} "
                        f"L:{candle[3]} C:{candle[4]} V:{candle[6]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_depth(market: Market, pair: str, count: int = 100) -> str:
    """Get order book."""
    try:
        result = market.get_order_book(pair=pair, count=count)
        if not result or pair not in result:
            return f"No order book for {pair}."

        # Data is nested under pair key
        pair_data = result.get(pair, {})
        bids = pair_data.get("bids", [])[:10]
        asks = pair_data.get("asks", [])[:10]
        lines = [f"=== Order Book {pair} ==="]

        lines.append("  ASKS (selling)")
        for ask in asks:
            lines.append(f"    ${ask[0]:>10s} x {ask[1]}")

        lines.append("  BIDS (buying)")
        for bid in bids:
            lines.append(f"    ${bid[0]:>10s} x {bid[1]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_recent_trades(market: Market, pair: str, count: int = 20) -> str:
    """Get recent trades."""
    try:
        result = market.get_recent_trades(pair=pair)
        if not result or pair not in result:
            return f"No trades for {pair}."

        # Data is a list under pair key: [price, volume, time, buy/sell, market/limit, misc, trade_id]
        trades = result.get(pair, [])[:count]
        lines = [f"=== Recent Trades {pair} ==="]
        for trade in trades:
            timestamp = datetime.fromtimestamp(float(trade[2]))
            side = "BUY" if trade[3] == "b" else "SELL"
            lines.append(f"  [{side:4s}] {timestamp.strftime('%Y-%m-%d %H:%M')} ${trade[0]} x {trade[1]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_spreads(market: Market, pair: str, count: int = 20) -> str:
    """Get recent spreads."""
    try:
        result = market.get_recent_spreads(pair=pair)
        if not result or pair not in result:
            return f"No spreads for {pair}."

        spreads = result.get(pair, [])
        lines = [f"=== Recent Spreads {pair} ==="]
        # Spread data is [time, bid, ask]
        for spread in spreads[-count:]:
            timestamp = datetime.fromtimestamp(float(spread[0]))
            bid = spread[1]
            ask = spread[2]
            spread_val = float(ask) - float(bid)
            lines.append(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} ${bid} - ${ask} (spread: ${spread_val:.2f})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_status(market: Market) -> str:
    """Get system status."""
    try:
        result = market.get_system_status()
        if not result:
            return "No status data."

        status = result.get("status", "?")
        messages = result.get("messages", [])
        lines = [f"=== System Status: {status} ==="]
        for msg in messages:
            lines.append(f"  {msg}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_time() -> str:
    """Get server time (via direct API call since SDK doesn't expose it)."""
    try:
        import urllib.request
        import json
        req = urllib.request.Request("https://api.kraken.com/0/public/Time")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        if result.get("error"):
            return f"Error: {result['error']}"

        data = result.get("result", {})
        timestamp = float(data.get("unixtime", 0))
        rfc1123 = data.get("rfc1123", "")
        dt = datetime.fromtimestamp(timestamp)
        lines = [f"=== Server Time ==="]
        lines.append(f"  Unix: {int(timestamp)}")
        lines.append(f"  UTC:  {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  RFC:  {rfc1123}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


# ============ STAKING (PRIVATE) ============

def cmd_earn(earn: Optional[Earn], positions: bool = False) -> str:
    """Get staking/earn positions."""
    if not earn:
        return "Error: API credentials required for this command."
    try:
        if positions:
            result = earn.list_earn_allocations(converted_asset="USD", hide_zero_allocations="true")
            if not result or "items" not in result or not result.get("items"):
                return "No earn allocations found."

            total_allocated = result.get("total_allocated", "0")
            total_rewarded = result.get("total_rewarded", "0")

            lines = [f"=== Earn Allocations (USD) ==="]
            lines.append(f"  Total Allocated: ${total_allocated}")
            lines.append(f"  Total Rewarded:  ${total_rewarded}")
            lines.append("")

            for item in result.get("items", []):
                asset = item.get("native_asset", "?")
                allocated = item.get("amount_allocated", {}).get("total", {}).get("converted", "0")
                rewarded = item.get("total_rewarded", {}).get("converted", "0")
                lines.append(f"  {asset:6s}: ${allocated:>10s} allocated, ${rewarded:>6s} rewarded")

            return "\n".join(lines)
        else:
            return "Run 'earn positions' to see current staking positions."
    except Exception as e:
        return f"Error: {e}"


def cmd_earn_status(earn: Optional[Earn], strategy_id: Optional[str] = None) -> str:
    """Get pending stake allocation status."""
    if not earn:
        return "Error: API credentials required for this command."
    try:
        if not strategy_id:
            # List allocations which includes pending status
            result = earn.list_earn_allocations(converted_asset="USD", hide_zero_allocations="false")
            if not result or "items" not in result:
                return "No earn allocations."

            lines = ["=== Earn Allocations with Status ==="]
            for item in result.get("items", []):
                asset = item.get("native_asset", "?")
                allocated = item.get("amount_allocated", {}).get("total", {}).get("converted", "0")
                pending = item.get("pending_amount", "0")
                lines.append(f"  {asset}: ${allocated} allocated, ${pending} pending")
            return "\n".join(lines)

        result = earn.get_allocation_status(strategy_id=strategy_id)
        if not result or "status" not in result:
            return f"No status for strategy {strategy_id}"

        lines = [f"=== Allocation Status for {strategy_id} ==="]
        for status in result.get("status", []):
            lines.append(f"  ID: {status.get('allocation_id', '?')}")
            lines.append(f"  Asset: {status.get('asset', '?')}")
            lines.append(f"  Amount: {status.get('amount', '?')}")
            lines.append(f"  Status: {status.get('status', '?')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_earn_dealloc_status(earn: Optional[Earn], strategy_id: Optional[str] = None) -> str:
    """Get pending unstake deallocation status."""
    if not earn:
        return "Error: API credentials required for this command."
    if not strategy_id:
        return "Error: --refid (strategy_id) required for earn-dealloc-status"
    try:
        result = earn.get_deallocation_status(strategy_id=strategy_id)
        if not result or "status" not in result or not result.get("status"):
            return "No pending deallocations."

        lines = ["=== Earn Deallocation Status ==="]
        for status in result.get("status", []):
            lines.append(f"  ID: {status.get('deallocation_id', '?')}")
            lines.append(f"  Asset: {status.get('asset', '?')}")
            lines.append(f"  Amount: {status.get('amount', '?')}")
            lines.append(f"  Status: {status.get('status', '?')}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def cmd_earn_strategies(earn: Optional[Earn]) -> str:
    """List available earn strategies."""
    if not earn:
        return "Error: API credentials required for this command."
    try:
        result = earn.list_earn_strategies()
        if not result or "items" not in result or not result.get("items"):
            return "No earn strategies available."

        lines = ["=== Earn Strategies ==="]
        for strat in result.get("items", []):
            lines.append(f"  Strategy: {strat.get('id', '?')}")
            lines.append(f"  Asset: {strat.get('asset', '?')}")
            apr = strat.get('apr_estimate', {}).get('high', '?')
            lines.append(f"  APR: {apr}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


# ============ DEPOSITS (PRIVATE) ============

def cmd_deposits(funding: Optional[Funding], asset: Optional[str] = None, address: bool = False) -> str:
    """Get deposit methods or address."""
    if not funding:
        return "Error: API credentials required for this command."
    target_asset = asset or "BTC"
    try:
        if address:
            result = funding.get_deposit_address(asset=target_asset, method="")
            if not result:
                return f"No deposit address found for {target_asset}."

            lines = [f"=== Deposit Address for {target_asset} ==="]
            for addr in result:
                lines.append(f"  Address: {addr.get('address', '?')}")
                if addr.get('tag'):
                    lines.append(f"  Tag: {addr.get('tag')}")
            return "\n".join(lines)
        else:
            result = funding.get_deposit_methods(asset=target_asset)
            if not result:
                return "No deposit methods found."

            lines = [f"=== Deposit Methods ({target_asset}) ==="]
            for method in result:
                lines.append(f"  {method.get('method', '?'):20s}: {method.get('description', '?')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description="Kraken Crypto CLI")
    parser.add_argument("command", choices=[
        "balance", "balance-ex", "portfolio", "open-orders", "closed-orders", "orders", "trades", "query-trades",
        "open-positions", "ledger", "query-ledger", "volume",
        "earn", "earn-positions", "earn-status", "earn-dealloc-status", "earn-strategies",
        "ticker", "assets", "pairs", "ohlc", "depth", "recent-trades", "spreads", "status", "time",
        "deposits-methods", "deposits-address"
    ], help="Command to run")
    parser.add_argument("--asset", help="Filter by asset (for ledger, deposits)")
    parser.add_argument("--pair", help="Filter by trading pair")
    parser.add_argument("--limit", type=int, default=20, help="Limit results")
    parser.add_argument("--refid", help="Reference ID for query commands")
    parser.add_argument("--interval", type=int, default=1440, help="OHLC interval in minutes")
    parser.add_argument("--count", type=int, default=100, help="Order book/trades count")

    args = parser.parse_args()

    user, market, earn, funding = get_clients()

    if args.command == "balance":
        print(cmd_balance(user))
    elif args.command == "balance-ex":
        print(cmd_balance_ex(user))
    elif args.command == "portfolio":
        print(cmd_portfolio(user))
    elif args.command == "open-orders":
        print(cmd_open_orders(user))
    elif args.command == "closed-orders":
        print(cmd_closed_orders(user, args.limit))
    elif args.command == "orders":
        print(cmd_query_orders(user, args.refid))
    elif args.command == "trades":
        print(cmd_trades(user, args.limit))
    elif args.command == "query-trades":
        print(cmd_query_trades(user, args.refid))
    elif args.command == "open-positions":
        print(cmd_open_positions(user))
    elif args.command == "ledger":
        print(cmd_ledger(user, args.asset, args.limit))
    elif args.command == "query-ledger":
        print(cmd_query_ledger(user, args.refid))
    elif args.command == "volume":
        print(cmd_volume(user))
    elif args.command == "ticker":
        if not args.pair:
            print("Error: --pair required for ticker")
            sys.exit(1)
        print(cmd_ticker(market, args.pair))
    elif args.command == "assets":
        print(cmd_assets(market))
    elif args.command == "pairs":
        print(cmd_asset_pairs(market))
    elif args.command == "ohlc":
        if not args.pair:
            print("Error: --pair required for ohlc")
            sys.exit(1)
        print(cmd_ohlc(market, args.pair, args.interval))
    elif args.command == "depth":
        if not args.pair:
            print("Error: --pair required for depth")
            sys.exit(1)
        print(cmd_depth(market, args.pair, args.count))
    elif args.command == "recent-trades":
        if not args.pair:
            print("Error: --pair required for recent-trades")
            sys.exit(1)
        print(cmd_recent_trades(market, args.pair, args.count))
    elif args.command == "spreads":
        if not args.pair:
            print("Error: --pair required for spreads")
            sys.exit(1)
        print(cmd_spreads(market, args.pair, args.count))
    elif args.command == "status":
        print(cmd_status(market))
    elif args.command == "time":
        print(cmd_time())
    elif args.command == "earn":
        print(cmd_earn(earn, positions=False))
    elif args.command == "earn-positions":
        print(cmd_earn(earn, positions=True))
    elif args.command == "earn-status":
        print(cmd_earn_status(earn, args.refid))
    elif args.command == "earn-dealloc-status":
        print(cmd_earn_dealloc_status(earn, args.refid))
    elif args.command == "earn-strategies":
        print(cmd_earn_strategies(earn))
    elif args.command == "deposits-methods":
        print(cmd_deposits(funding, asset=args.asset, address=False))
    elif args.command == "deposits-address":
        if not args.asset:
            print("Error: --asset required for deposits-address")
            sys.exit(1)
        print(cmd_deposits(funding, asset=args.asset, address=True))


if __name__ == "__main__":
    main()
