# 📈 Crypto Price & Chart

A Clawdbot skill for fetching cryptocurrency token prices and generating beautiful candlestick charts.

## Features

- 🚀 **Fast price lookup** via CoinGecko and Hyperliquid APIs
- 📊 **Candlestick charts** with dark theme (8x8 square format)
- ⚡ **Smart caching** (5-minute TTL for price data)
- 🎯 **Multiple data sources** (Hyperliquid preferred for supported tokens, CoinGecko fallback)
- 📱 **Flexible timeframes** (30m, 3h, 12h, 24h, 2d)

## Installation

### Via ClawdHub

```bash
clawdhub install evgyur/crypto-price
```

### Manual Installation

1. Clone or copy this skill to your Clawdbot workspace:
   ```bash
   cd ~/.clawdbot/workspace/skills
   git clone https://github.com/evgyur/crypto-price.git
   ```

2. Ensure Python 3 is installed:
   ```bash
   python3 --version
   ```

3. Install required Python packages:
   ```bash
   pip install matplotlib
   ```

4. Verify installation:
   ```bash
   clawdbot skills info crypto-price
   ```

## Usage

### As a Skill

The skill is automatically triggered when users ask for:
- Token prices
- Crypto charts
- Cryptocurrency market data

### Direct Script Usage

```bash
python3 scripts/get_price_chart.py <SYMBOL> [duration]
```

**Examples:**
```bash
# Get HYPE price and 24h chart
python3 scripts/get_price_chart.py HYPE

# Get Bitcoin price and 12h chart
python3 scripts/get_price_chart.py BTC 12h

# Get Ethereum price and 3h chart
python3 scripts/get_price_chart.py ETH 3h

# Get Solana price and 30m chart
python3 scripts/get_price_chart.py SOL 30m

# Get Cardano price and 2d chart
python3 scripts/get_price_chart.py ADA 2d
```

### Duration Format

- `30m` - 30 minutes
- `3h` - 3 hours
- `12h` - 12 hours
- `24h` - 24 hours (default)
- `2d` - 2 days

## Output Format

The script returns JSON with the following structure:

```json
{
  "symbol": "BTC",
  "token_id": "bitcoin",
  "source": "coingecko",
  "currency": "USD",
  "hours": 24.0,
  "duration_label": "24h",
  "candle_minutes": 15,
  "price": 89946.00,
  "price_usdt": 89946.00,
  "change_period": -54.00,
  "change_period_percent": -0.06,
  "chart_path": "/tmp/crypto_chart_BTC_1769142011.png",
  "text": "BTC: $89946.00 USD (-0.06% over 24h)",
  "text_plain": "BTC: $89946.00 USD (-0.06% over 24h)"
}
```

## Chart Generation

- **Type**: Candlestick (OHLC)
- **Size**: 8x8 inches (square format)
- **Theme**: Dark (#121212 background)
- **Colors** (default mode): 
  - Grey (#B0B0B0 / #606060) normal candles
  - Cyan (#00FFFF) bullish swing reversals (3 candles after swing low)
  - Magenta (#FF00FF) bearish swing reversals (3 candles after swing high)
  - Gold (#FFD54F) / Light Blue (#90CAF9) absolute high/low markers
- **Colors** (gradient mode, add `gradient` flag): 
  - Green gradient (#84dc58 → #336d16) bullish candles
  - Blue-purple gradient (#6c7ce4 → #544996) bearish candles
- **Features**:
  - Fractal swing high/low detection (true pivots, configurable window)
  - Volume bars (when available from API)
  - Last price highlighted on Y-axis
  - Tomorrow font for crisp rendering
- **Output**: PNG files saved to `/tmp/crypto_chart_{SYMBOL}_{timestamp}.png`

## Data Sources

1. **Hyperliquid API** (`https://api.hyperliquid.xyz/info`)
   - Preferred for HYPE and other Hyperliquid tokens
   - Provides real-time price data and candlestick data

2. **CoinGecko API** (`https://api.coingecko.com/api/v3/`)
   - Fallback for all other tokens
   - Supports price lookup, market charts, and OHLC data

## Caching

Price data is cached for 300 seconds (5 minutes) to reduce API calls:
- Cache files: `/tmp/crypto_price_*.json`
- Automatic cache invalidation after TTL

## Supported Tokens

Works with any token supported by CoinGecko or Hyperliquid:
- **Popular tokens**: BTC, ETH, SOL, ADA, DOT, LINK, MATIC, AVAX, ATOM, ALGO, XLM, XRP, LTC, BCH, ETC, TRX, XMR, DASH, ZEC, EOS, BNB, DOGE, SHIB, UNI, AAVE
- **Hyperliquid tokens**: HYPE, and other tokens listed on Hyperliquid

## Requirements

- Python 3.6+
- `matplotlib` library
- Internet connection for API calls

## Dependencies

```bash
pip install matplotlib
```

## License

MIT

## Author

Created for Clawdbot community. Originally part of Clawdbot bundled skills, restored and enhanced.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Related Skills

This skill works with slash command skills:
- `/hype` - HYPE token price and chart
- `/token <SYMBOL>` - Any token price and chart
- `/btc`, `/eth`, `/sol`, etc. - Popular tokens

## Links

- [GitHub Repository](https://github.com/evgyur/crypto-price)
- [ClawdHub](https://clawdhub.com/evgyur/crypto-price)
- [Clawdbot Documentation](https://docs.clawd.bot)

## Changelog

### v1.0.0
- Initial release
- Support for CoinGecko and Hyperliquid APIs
- Candlestick chart generation
- Smart caching system
- Multiple timeframe support
