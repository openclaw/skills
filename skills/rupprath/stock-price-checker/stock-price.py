#!/usr/bin/env python3
"""
Stock Price Checker - Get current stock prices from Yahoo Finance using yfinance.
"""

import sys
import yfinance as yf

def format_number(num, decimals=2):
    """Format a number with commas and specified decimals."""
    if num is None:
        return "N/A"
    return f"{num:,.{decimals}f}"

def get_stock_price(symbol: str) -> dict:
    """Get current stock price for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        change = current_price - previous_close if current_price and previous_close else None
        change_percent = ((change / previous_close) * 100) if change and previous_close else None
        market_cap = info.get('marketCap')
        volume = info.get('volume')
        avg_volume = info.get('averageVolume')
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')

        return {
            "symbol": symbol,
            "price": current_price,
            "change": change,
            "change_percent": change_percent,
            "previous_close": previous_close,
            "market_cap": market_cap,
            "volume": volume,
            "avg_volume": avg_volume,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low
        }
    except Exception as e:
        return {
            "error": f"Could not get stock price for {symbol}: {str(e)}"
        }

def format_output(data: dict) -> str:
    """Format stock data in the desired output format."""
    if "error" in data:
        return f"Error: {data['error']}"

    symbol = data['symbol']
    price = data['price']
    change = data['change']
    change_percent = data['change_percent']
    volume = data['volume']
    avg_volume = data['avg_volume']

    # Format price
    price_str = f"${format_number(price)}"

    # Format change with arrow
    if change is not None and change > 0:
        change_str = f"▲${format_number(change)}"
    elif change is not None and change < 0:
        change_str = f"▼${format_number(abs(change))}"
    else:
        change_str = "—"

    # Format change percent
    if change_percent is not None:
        change_percent_str = f"({format_number(change_percent)}%)"
    else:
        change_percent_str = "(—)"

    # Format volume
    if volume is not None:
        volume_str = f"Vol: {format_number(volume / 1_000_000, 1)}M"
    else:
        volume_str = "Vol: N/A"

    # Format average volume
    if avg_volume is not None:
        avg_volume_str = f"Avg: {format_number(avg_volume / 1_000_000, 1)}M"
    else:
        avg_volume_str = "Avg: N/A"

    # Calculate percentage of average volume
    if volume is not None and avg_volume is not None and avg_volume > 0:
        volume_percent = (volume / avg_volume) * 100
        volume_percent_str = f"| {format_number(volume_percent, 0)}% of avg"
    else:
        volume_percent_str = ""

    # Combine all parts
    output = f"{symbol}: {price_str} {change_str} {change_percent_str} {volume_str} {avg_volume_str} {volume_percent_str}"
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: stock-price <SYMBOL>")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    result = get_stock_price(symbol)
    print(format_output(result))

if __name__ == "__main__":
    main()