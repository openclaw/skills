# @cyberdrk/onchain

CLI for crypto portfolio tracking, market data, and CEX history. Designed for both human use and AI agent integration.

## Installation

```bash
npm install -g @cyberdrk/onchain
```

Or run directly with npx:
```bash
npx @cyberdrk/onchain price btc
```

## Quick Start

```bash
# Check token prices
onchain price btc
onchain price eth sol matic

# View wallet balances (auto-detects EVM/Solana)
onchain balance 0x1234...5678

# CEX balances
onchain coinbase balance
onchain binance balance

# Market overview
onchain markets

# Prediction markets
onchain polymarket trending
```

## Commands

### Market Data
```bash
onchain price <token>           # Token price with 24h change
onchain markets                 # Market overview with trending coins
```

### Wallet Data
```bash
onchain balance <address>       # Token balances (EVM or Solana)
onchain history <address>       # Transaction history
onchain portfolio <address>     # Full portfolio with DeFi positions
```

### CEX Data
```bash
onchain coinbase balance        # Coinbase account balances
onchain coinbase history        # Trade history
onchain binance balance         # Binance account balances
onchain binance history         # Trade history
```

### Prediction Markets
```bash
onchain polymarket trending     # Trending markets
onchain polymarket search <q>   # Search markets
onchain polymarket view <slug>  # Market details
```

### Configuration
```bash
onchain setup                   # Interactive API key setup
onchain config                  # View current configuration
onchain test                    # Test all configured providers
```

## Configuration

Run `onchain setup` for interactive configuration, or set environment variables:

| Feature | Environment Variable | Provider |
|---------|---------------------|----------|
| EVM wallets | `DEBANK_API_KEY` | [DeBank Cloud](https://cloud.debank.com/) |
| Solana wallets | `HELIUS_API_KEY` | [Helius](https://helius.xyz/) |
| Coinbase | `COINBASE_API_KEY_ID` + `COINBASE_API_KEY_SECRET` | [Coinbase CDP](https://portal.cdp.coinbase.com/) |
| Binance | `BINANCE_API_KEY` + `BINANCE_API_SECRET` | [Binance](https://www.binance.com/en/my/settings/api-management) |
| Market data | `COINGECKO_API_KEY` | [CoinGecko](https://www.coingecko.com/en/api) (optional) |
| Market fallback | `COINMARKETCAP_API_KEY` | [CoinMarketCap](https://coinmarketcap.com/api/) (optional) |

Config file locations:
- Global: `~/.config/onchain/config.json5`
- Local: `./.onchainrc.json5`

## Global Options

```bash
--json              # Output as JSON (for scripting/agents)
--plain             # Disable colors and emoji
--no-color          # Disable colors only
--timeout <ms>      # Request timeout in milliseconds
```

## Agent Integration

This CLI is designed for AI agent use with `--json` output:

```bash
# Get portfolio value
onchain --json portfolio 0x123... | jq '.totalValueUsd'

# Check if market is up
onchain --json markets | jq '.marketCapChange24h > 0'

# Get specific token price
onchain --json price eth | jq '{price: .priceUsd, change: .priceChange24h}'
```

Exit codes: `0` for success, `1` for errors.

## Supported Chains

**EVM (via DeBank):** Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Avalanche, Base, zkSync Era, Linea, Scroll, Blast, Mantle, and 60+ more.

**Solana (via Helius):** Full mainnet support including SPL tokens and NFTs.

## Development

```bash
pnpm install
pnpm run dev price btc    # Run without building
pnpm run build            # Build TypeScript
pnpm run test             # Run tests
pnpm run lint             # Lint code
```

## License

MIT
