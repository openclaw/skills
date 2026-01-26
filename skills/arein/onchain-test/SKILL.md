---
name: onchain
description: CLI for crypto portfolio tracking, market data, and CEX history. Use when the user asks about crypto prices, wallet balances, portfolio values, Coinbase/Binance holdings, or Polymarket predictions.
---

# Onchain CLI

CLI for crypto portfolio tracking, market data, and CEX history.

## Invocation

```
onchain <command>
```

## Commands

### Market Data

```bash
onchain price <token>         # Token price (btc, eth, sol, etc.)
onchain markets               # Market overview with trending
```

### Wallet Data

```bash
onchain balance [address]           # Token balances (auto-detects EVM/Solana)
onchain balance --chain polygon     # Filter by chain
onchain history [address]           # Transaction history
onchain portfolio [address]         # Full portfolio with DeFi positions
```

### CEX Data

```bash
onchain coinbase balance      # Coinbase balances
onchain coinbase history      # Coinbase trade history
onchain binance balance       # Binance balances
onchain binance history       # Binance trade history
```

### Prediction Markets

```bash
onchain polymarket trending          # Trending markets
onchain polymarket search <query>    # Search markets
onchain polymarket view <slug>       # View market details
```

### Configuration

```bash
onchain setup                 # Interactive setup wizard
onchain config                # View current config
onchain config wallet add <name> <address>
onchain config wallet set-default <name>
```

## Global Options

- `--json` - Output as JSON (agent-friendly)
- `--plain` - Disable colors and emoji
- `--timeout <ms>` - Request timeout

## Configuration

Config file: `~/.config/onchain/config.json5`

### Required API Keys

| Feature | API Key | Get Key |
|---------|---------|---------|
| EVM wallets | `DEBANK_API_KEY` | [DeBank](https://cloud.debank.com/) |
| Solana wallets | `HELIUS_API_KEY` | [Helius](https://helius.xyz/) |
| Coinbase CEX | `COINBASE_API_KEY` + `COINBASE_API_SECRET` | [Coinbase](https://www.coinbase.com/settings/api) |
| Binance CEX | `BINANCE_API_KEY` + `BINANCE_API_SECRET` | [Binance](https://www.binance.com/en/my/settings/api-management) |

### Optional API Keys

| Feature | API Key | Notes |
|---------|---------|-------|
| Market data | `COINGECKO_API_KEY` | Free tier works, Pro for higher limits |
| Market fallback | `COINMARKETCAP_API_KEY` | Alternative market data source |

## Examples

### Get Bitcoin price
```bash
onchain price btc
```

### Check wallet balance
```bash
onchain balance 0x1234...5678
```

### View portfolio with DeFi positions
```bash
onchain portfolio main  # Uses saved wallet named "main"
```

### Get trending prediction markets
```bash
onchain polymarket trending -n 5
```

### JSON output for scripts
```bash
onchain --json price eth | jq '.priceUsd'
```

## Supported Chains

### EVM (via DeBank)
Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Avalanche, Base, zkSync Era, Linea, Scroll, Blast, Mantle, Gnosis, Fantom, Celo, and more.

### Solana (via Helius)
Full Solana mainnet support including SPL tokens and NFTs.

## Agent Integration

This CLI is designed for agent use. Key patterns:

1. **Always use `--json`** for programmatic access
2. **Check exit codes** - 0 for success, 1 for error
3. **Use saved wallets** - Configure once with `onchain setup`, reference by name
4. **Rate limiting** - APIs have rate limits, add delays between rapid calls

### Example Agent Usage

```bash
# Get portfolio value
VALUE=$(onchain --json portfolio main | jq -r '.totalValueUsd')

# Get price with change
onchain --json price btc | jq '{price: .priceUsd, change24h: .priceChange24h}'

# Check if market is bullish
CHANGE=$(onchain --json markets | jq '.marketCapChange24h')
```
