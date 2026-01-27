---
name: onchain
description: CLI for crypto portfolio tracking, market data, CEX history, and transaction lookups. Use when the user asks about crypto prices, wallet balances, portfolio values, Coinbase/Binance holdings, Polymarket predictions, or transaction details.
---

# Onchain CLI

CLI for crypto portfolio tracking, market data, and CEX history.

## First-Time Setup (Required)

Before using most features, users must configure their API keys:

```bash
onchain setup
```

This interactive wizard helps configure:
- **Coinbase/Binance** - For CEX balances and trade history
- **DeBank** - For EVM wallet data (Ethereum, Polygon, Arbitrum, etc.)
- **Helius** - For Solana wallet data

**Without setup**: Only `onchain price` and `onchain markets` work (using free CoinGecko tier).

**Verify setup**: Run `onchain test` to check which providers are configured and working.

**Agent note**: If a command fails with "not configured" or "API key required", guide the user to run `onchain setup` first, then `onchain test` to verify.

## Invocation

```
onchain <command>
```

## Commands

### Market Data

```bash
onchain price <token>         # Token price (btc, eth, sol, etc.)
onchain markets               # Market overview with trending
onchain search <query>        # Search tokens by name or symbol
onchain gas                   # Current gas prices (Ethereum default)
onchain gas --chain polygon   # Gas prices for other EVM chains
```

### Wallet Data

```bash
onchain balance [address]           # Token balances (auto-detects EVM/Solana)
onchain balance --chain polygon     # Filter by chain
onchain history [address]           # Transaction history
onchain portfolio [address]         # Full portfolio with DeFi positions
```

### Transaction Lookup

```bash
onchain tx <hash>                   # Lookup transaction details (auto-detects chain)
onchain tx <hash> --chain base      # Specify chain explicitly
onchain tx <explorer-url>           # Paste block explorer URL directly
```

Supports EVM chains (Ethereum, Polygon, Base, Arbitrum, Optimism, BSC, Avalanche, Fantom) and Solana. Accepts raw hashes or explorer URLs (etherscan.io, basescan.org, solscan.io, etc.).

#### Example Output
```
Transaction Details

✓ Status: SUCCESS
  Hash:  0xd757...5f31
  Chain: Base
  Block: 41,310,593
  Time:  Jan 26, 2026, 01:55 PM (4h ago)

Addresses
  From: 0xc4e7263dd870a29f1cfe438d1a7db48547b16888
  To:   0xab98b760e5ad88521a97c0f87a3f6eef8c42641d

Value & Fee
  Value: 0 ETH
  Fee:   3.62e-7 ETH
  Gas:   96,893 / 249,604 (39%)

Method
  ID: 0x6a761202

🔗 https://basescan.org/tx/0xd757...
```

**This output contains all available transaction data.** The CLI queries Etherscan/Solscan APIs directly - there is no additional data available from other sources.

### CEX Data

```bash
onchain coinbase balance      # Coinbase balances
onchain coinbase history      # Coinbase trade history
onchain binance balance       # Binance balances
onchain binance history       # Binance trade history
```

### Prediction Markets

```bash
onchain polymarket tags              # List all available tags/categories
onchain polymarket tags --popular    # Show popular tags by market count
onchain polymarket trending          # Trending markets (respects config filters)
onchain polymarket trending --all    # Show all markets (ignore config filters)
onchain polymarket trending --exclude sports,nfl   # Exclude specific tags
onchain polymarket trending --include crypto,ai    # Only show specific tags
onchain polymarket search <query>    # Search markets (respects config filters)
onchain polymarket view <slug>       # View market details
onchain polymarket sentiment <topic> # Analyze market sentiment for a topic
```

**Sentiment analysis**: Analyzes prediction markets to determine bullish/bearish expectations:
```bash
onchain polymarket sentiment fed        # Fed rate expectations
onchain polymarket sentiment bitcoin    # Bitcoin market sentiment
onchain polymarket sentiment ai         # AI-related predictions
onchain polymarket sentiment trump      # Political sentiment
onchain polymarket sentiment fed --json # JSON output for agents
```

**Tag filtering**: Configure default excludes in `~/.config/onchain/config.json5`:
```json5
{
  "polymarket": {
    "excludeTags": ["sports", "nfl", "nba", "mlb"],
    "includeTags": []  // empty = all non-excluded
  }
}
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
| EVM tx lookup | `ETHERSCAN_API_KEY` | For `onchain tx` on EVM chains |
| Solana tx lookup | `SOLSCAN_API_KEY` | For `onchain tx` on Solana |

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
onchain polymarket trending -n 5             # Top 5 (respects config filters)
onchain polymarket trending --all            # All markets, ignore config
onchain polymarket trending --exclude sports # Filter out sports on-the-fly
```

### Lookup a transaction
```bash
onchain tx 0xd757e7e4cdb424e22319cbf63bbcfcd4b26c93ebef31d1458ab7d5e986375f31
onchain tx https://basescan.org/tx/0x...  # Or paste explorer URL
```

### Search for tokens
```bash
onchain search pepe               # Find tokens matching "pepe"
onchain search "shiba inu" -l 5   # Limit to 5 results
```

### Check gas prices
```bash
onchain gas                   # Ethereum gas prices
onchain gas --chain polygon   # Polygon gas prices
onchain gas --json            # JSON output
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

# Get transaction details as JSON
TX=$(onchain --json tx 0x... --chain base)
echo $TX | jq '{status: .status, from: .from, to: .to, method: .methodId}'
```

### Transaction Lookup Guidance

**IMPORTANT: Trust the CLI output.** The `onchain tx` command queries Etherscan (EVM) or Solscan (Solana) APIs directly and returns all available data.

**DO NOT:**
- Use curl to hit Etherscan/Basescan APIs directly
- Use `cast` or other CLI tools as "fallbacks"
- Use WebFetch to scrape block explorer websites
- Assume the CLI is missing data - it returns everything available

**DO:**
- Use `onchain tx <hash>` or `onchain tx <explorer-url>`
- Use `--json` for structured data parsing
- Interpret the output directly to answer user questions

**Example interpretation:**
```bash
onchain tx 0x... --chain base
```
If output shows `Status: SUCCESS`, `From: 0x...`, `To: 0x...`, `Method ID: 0x6a761202` - that's a successful contract interaction. The method ID `0x6a761202` is `execTransaction` (Gnosis Safe). No additional lookups needed.
