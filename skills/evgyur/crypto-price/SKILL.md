---
name: crypto-price
description: Get cryptocurrency token price and generate candlestick charts via CoinGecko API or Hyperliquid API. Use when user asks for token price, crypto price, price chart, or cryptocurrency market data.
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3"]}}}
---

# Crypto Price & Chart

Get cryptocurrency token price and generate candlestick charts.

## Usage

Execute the script with token symbol and optional duration:

```bash
python3 {baseDir}/scripts/get_price_chart.py <SYMBOL> [duration]
```

**Examples:**
- `python3 {baseDir}/scripts/get_price_chart.py HYPE`
- `python3 {baseDir}/scripts/get_price_chart.py HYPE 12h`
- `python3 {baseDir}/scripts/get_price_chart.py BTC 3h`
- `python3 {baseDir}/scripts/get_price_chart.py ETH 30m`
- `python3 {baseDir}/scripts/get_price_chart.py SOL 2d`

**Duration format:** `30m`, `3h`, `12h`, `24h` (default), `2d`

## Output

Returns JSON with:
- `price` - Current price in USD/USDT
- `change_period_percent` - Price change percentage for the period
- `chart_path` - Path to generated PNG chart (if available)
- `text_plain` - Formatted text description

**Chart as image (always when chart_path is present):**  
You must send the chart as a **photo**, not as text. In your reply, output `text_plain` and on a new line: `MEDIA: ` followed by the exact `chart_path` value (e.g. `MEDIA: /tmp/crypto_chart_HYPE_1769204734.png`). Clawdbot will attach that file as an image. Do **not** write `[chart: path]` or any other text placeholder — only the `MEDIA: <chart_path>` line makes the image appear.

## Chart Details

- Format: Candlestick chart (8x8 square)
- Theme: Dark (#0f141c background)
- Output: `/tmp/crypto_chart_{SYMBOL}_{timestamp}.png`

## Data Sources

1. **Hyperliquid API** - For HYPE and other Hyperliquid tokens (preferred)
2. **CoinGecko API** - Fallback for other tokens

Price data cached for 300 seconds (5 minutes) in `/tmp/crypto_price_*.json`.
