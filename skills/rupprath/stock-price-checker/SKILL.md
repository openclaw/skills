---
name: stock-price-checker
description: Check stock prices using yfinance library. No API key required.
homepage: https://finance.yahoo.com
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","yfinance"]}}}
---

# Stock Price Checker

Get current stock prices from Yahoo Finance using the yfinance library.

## Quick Commands

```bash
cd skills/stock-price-checker

# Check stock price
python3 stock-price.py NVDA

# Check another stock
python3 stock-price.py AAPL
```

## Usage Examples

**Check NVIDIA stock:**
```bash
python3 stock-price.py NVDA
```

**Check VOO (S&P 500 ETF):**
```bash
python3 stock-price.py VOO
```

**Check QQQ (Nasdaq-100 ETF):**
```bash
python3 stock-price.py QQQ
```

**Check any stock symbol:**
```bash
python3 stock-price.py TSLA
python3 stock-price.py MSFT
python3 stock-price.py AAPL
```

## Output Format

```json
{
  "symbol": "NVDA",
  "price": 189.52,
  "change": 3.05,
  "change_percent": 1.64,
  "previous_close": 186.47,
  "market_cap": 4614243483648,
  "volume": 112439494,
  "fifty_two_week_high": 212.19,
  "fifty_two_week_low": 86.62
}
```

## Technical Notes

- Uses yfinance library to fetch data from Yahoo Finance
- No API key required
- Handles errors gracefully
- Works with most major stocks and ETFs
- Returns comprehensive data including market cap, volume, and 52-week range

## Troubleshooting

- If the stock symbol is invalid, the script will return an error
- Some data (like market cap) may not be available for all symbols