#!/usr/bin/env python3
# /// script
# dependencies = [
#   "yfinance",
#   "rich",
#   "pandas",
#   "plotille",
#   "matplotlib",
#   "mplfinance"
# ]
# ///

import sys
import yfinance as yf
import pandas as pd
import plotille
import matplotlib.pyplot as plt
import mplfinance as mpf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import os

console = Console()

def get_ticker_info(symbol):
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info):
            if not info.get('symbol'): return None, None
        return ticker, info
    except:
        return None, None

def show_price(symbol, ticker, info):
    current = info.get('regularMarketPrice') or info.get('currentPrice')
    prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
    if current is None: return
    change = current - prev_close
    pct_change = (change / prev_close) * 100
    color = "green" if change >= 0 else "red"
    sign = "+" if change >= 0 else ""
    table = Table(title=f"Price: {info.get('longName', symbol)}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Symbol", symbol)
    table.add_row("Current Price", f"{current:,.2f} {info.get('currency', '')}")
    table.add_row("Change", f"[{color}]{sign}{change:,.2f} ({sign}{pct_change:.2f}%)[/{color}]")
    console.print(table)

def show_fundamentals(symbol, ticker, info):
    table = Table(title=f"Fundamentals: {info.get('longName', symbol)}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    metrics = [
        ("Market Cap", info.get('marketCap')),
        ("PE Ratio", info.get('forwardPE')),
        ("EPS", info.get('trailingEps')),
        ("ROE", info.get('returnOnEquity')),
    ]
    for name, val in metrics:
        table.add_row(name, str(val))
    console.print(table)

def show_history(symbol, ticker, period="1mo"):
    hist = ticker.history(period=period)
    chart = plotille.plot(hist.index, hist['Close'], height=15, width=60)
    console.print(Panel(chart, title=f"Chart: {symbol}", border_style="green"))

def save_pro_chart(symbol, ticker, period="3mo", chart_type='candle'):
    hist = ticker.history(period=period)
    if hist.empty: return None
    path = f"/tmp/{symbol}_pro.png"
    mc = mpf.make_marketcolors(up='red', down='blue', inherit=True)
    s  = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', y_on_right=True)
    mpf.plot(hist, type=chart_type, volume=True, 
             title=f"\n{symbol} Analysis ({period})",
             style=s, mav=(5, 20, 60), savefig=path)
    return path

def main():
    if len(sys.argv) < 2: sys.exit(1)
    
    cmd = sys.argv[1]
    symbol = sys.argv[2] if len(sys.argv) > 2 else None
    period = sys.argv[3] if len(sys.argv) > 3 else "3mo"
    chart_type = sys.argv[4] if len(sys.argv) > 4 else "candle"
    
    if not symbol:
        symbol = cmd
        cmd = "price"

    ticker, info = get_ticker_info(symbol)
    if not ticker: sys.exit(1)

    if cmd == "price": show_price(symbol, ticker, info)
    elif cmd == "fundamentals": show_fundamentals(symbol, ticker, info)
    elif cmd == "history": show_history(symbol, ticker, period=period)
    elif cmd == "pro":
        path = save_pro_chart(symbol, ticker, period=period, chart_type=chart_type)
        if path: print(f"CHART_PATH:{path}")
    elif cmd == "chart":
        hist = ticker.history(period=period)
        plt.figure(figsize=(10,6))
        plt.plot(hist.index, hist['Close'])
        path = f"/tmp/{symbol}_simple.png"
        plt.savefig(path)
        plt.close()
        print(f"CHART_PATH:{path}")
    else:
        show_price(symbol, ticker, info)

if __name__ == "__main__":
    main()
