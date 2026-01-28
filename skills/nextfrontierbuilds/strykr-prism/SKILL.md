---
name: strykr-prism
description: Real-time financial data API for AI agents. Stocks, crypto, forex, ETFs in one unified feed. Powers trading bots, market dashboards, and fintech apps. Alternative to Alpha Vantage, Polygon.io, CoinGecko. 120+ endpoints.
version: 1.1.0
keywords: finance-api, market-data, stock-api, crypto-api, trading-bot, real-time-data, alpha-vantage-alternative, polygon-alternative, coingecko-alternative, ai-trading, fintech, defi, ai, llm, cursor, claude, gpt, mcp, langchain, vibe-coding
---

# Finance Data API (Strykr PRISM)

**One API for all markets.** Real-time financial data for AI agents, trading bots, and fintech apps.

Powered by Strykr PRISM — unified data across crypto, stocks, ETFs, forex, commodities, and DeFi.

## Configuration

Set your PRISM API key:
```bash
export PRISM_API_KEY="your-api-key"
```

**Base URL:** `https://strykr-prism.up.railway.app`

## Quick Reference

### 🔍 Asset Resolution (Core Feature)

Resolve ANY asset identifier to canonical form:

```bash
# Resolve symbol (handles BTC, BTCUSD, XBT, bitcoin, etc.)
curl "$PRISM_URL/resolve/BTC"
curl "$PRISM_URL/resolve/BTCUSDT"
curl "$PRISM_URL/resolve/bitcoin"

# Natural language resolution (for agents)
curl -X POST "$PRISM_URL/agent/resolve" \
  -H "Content-Type: application/json" \
  -d '{"query": "price of ethereum"}'

# Batch resolve
curl -X POST "$PRISM_URL/resolve/batch" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC", "ETH", "AAPL", "GOLD"]}'

# Find trading venues for asset
curl "$PRISM_URL/resolve/venues/BTC"
```

### 💰 Price Data

```bash
# Crypto price
curl "$PRISM_URL/crypto/price/BTC"
curl "$PRISM_URL/crypto/price/ETH"

# Batch crypto prices
curl -X POST "$PRISM_URL/batch/crypto/prices" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC", "ETH", "SOL"]}'

# Stock quote
curl "$PRISM_URL/stocks/AAPL/quote"

# Batch stock quotes
curl -X POST "$PRISM_URL/stocks/batch/quotes" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"]}'
```

### 📊 Market Overview

```bash
# Full market overview (crypto + tradfi)
curl "$PRISM_URL/market/overview"

# Crypto global stats
curl "$PRISM_URL/crypto/global"

# Fear & Greed Index
curl "$PRISM_URL/market/fear-greed"

# Trending crypto
curl "$PRISM_URL/crypto/trending"

# Stock movers
curl "$PRISM_URL/stocks/gainers"
curl "$PRISM_URL/stocks/losers"
curl "$PRISM_URL/stocks/active"
```

### 🛡️ Token Security Analysis

```bash
# Analyze token for risks
curl "$PRISM_URL/analyze/BTC"

# Copycat/scam detection
curl "$PRISM_URL/analyze/copycat/PEPE"

# Check for rebrands (MATIC → POL)
curl "$PRISM_URL/analyze/rebrand/MATIC"

# Fork detection
curl "$PRISM_URL/analyze/fork/ETH"

# Holder analytics (whale concentration)
curl "$PRISM_URL/analytics/holders/0x1234..."
```

### 🔥 Trending & Discovery

```bash
# Trending crypto overall
curl "$PRISM_URL/crypto/trending"

# Solana Pump.fun bonding tokens (UNIQUE!)
curl "$PRISM_URL/crypto/trending/solana/bonding"

# Graduated from bonding curve
curl "$PRISM_URL/crypto/trending/solana/graduated"

# Trending DEX pools
curl "$PRISM_URL/crypto/trending/pools"

# EVM trending
curl "$PRISM_URL/crypto/trending/evm"

# Multi-day stock movers
curl "$PRISM_URL/stocks/multi-day-movers"
```

### 📈 DeFi & Derivatives

```bash
# DEX pairs
curl "$PRISM_URL/dex/pairs"

# Hyperliquid perps
curl "$PRISM_URL/dex/hyperliquid/pairs"
curl "$PRISM_URL/dex/hyperliquid/BTC/funding"
curl "$PRISM_URL/dex/hyperliquid/BTC/oi"

# Cross-venue funding rates
curl "$PRISM_URL/dex/BTC/funding/all"

# Cross-venue open interest
curl "$PRISM_URL/dex/BTC/oi/all"
```

### 💼 Wallet & On-Chain

```bash
# Wallet balances (multi-chain)
curl "$PRISM_URL/wallets/0xYourAddress/balances"

# Native balance only
curl "$PRISM_URL/wallets/0xYourAddress/native"

# Supported chains
curl "$PRISM_URL/chains"

# On-chain price
curl "$PRISM_URL/analytics/price/onchain/0xContractAddress"
```

### 🌍 Traditional Finance

```bash
# Forex rates
curl "$PRISM_URL/forex"
curl "$PRISM_URL/forex/USD/tradeable"

# Commodities
curl "$PRISM_URL/commodities"
curl "$PRISM_URL/commodities/GOLD/tradeable"

# ETFs
curl "$PRISM_URL/etfs/popular"

# Indexes
curl "$PRISM_URL/indexes"
curl "$PRISM_URL/indexes/sp500"
curl "$PRISM_URL/indexes/nasdaq100"

# Sectors
curl "$PRISM_URL/sectors"
```

### 🔧 System & Health

```bash
# API health
curl "$PRISM_URL/health"

# Data source status
curl "$PRISM_URL/crypto/sources/status"

# Registry health
curl "$PRISM_URL/registry/health"
```

## Use Cases

### Natural Language Price Lookup

When user asks "what's the price of bitcoin" or "how much is ETH":

1. Use `/agent/resolve` for natural language → canonical asset
2. Use `/crypto/price/{symbol}` or `/stocks/{symbol}/quote` for price
3. Return formatted response

### Token Security Check

When user asks "is this token safe" or "check 0x1234...":

1. Use `/analyze/{symbol}` for general analysis
2. Use `/analyze/copycat/{symbol}` for scam detection
3. Use `/analytics/holders/{contract}` for whale concentration
4. Return risk assessment

### Market Overview

When user asks "how's the market" or "what's trending":

1. Use `/market/overview` for full picture
2. Use `/market/fear-greed` for sentiment
3. Use `/crypto/trending` for hot coins
4. Use `/stocks/gainers` + `/losers` for stock movers

### Cross-Market Correlation

When user asks "what correlates with bitcoin":

1. Use `/market/overview` for cross-market data
2. Compare crypto vs stocks/commodities/forex
3. PRISM's 120+ endpoints enable true cross-market analysis

## Endpoint Speed Reference

| Endpoint | Speed | Use Case |
|----------|-------|----------|
| `/resolve/{symbol}` | 140-200ms | Symbol resolution |
| `/crypto/price/{symbol}` | 1.9-2.1s | Single price |
| `/market/fear-greed` | 229ms | Sentiment |
| `/crypto/trending` | 242ms | Hot coins |
| `/analyze/copycat/{symbol}` | 160ms | Scam detection |
| `/stocks/{symbol}/quote` | 214ms | Stock price |
| `/agent/resolve` | 3.4s | NL queries |

## Unique Data (Nobody Else Has)

- `/crypto/trending/solana/bonding` — Pump.fun launches
- `/analyze/copycat` — Scam/copycat detection
- `/analyze/rebrand` — Token migrations (MATIC→POL)
- `/dex/{symbol}/funding/all` — Cross-venue funding rates

## Example Responses

### Price Lookup
```
User: "price of bitcoin"
Response: "Bitcoin (BTC) is $43,250 (+2.1% 24h)"
```

### Security Check
```
User: "is PEPE safe"
Response: "🛡️ PEPE Analysis
• Risk Score: 35/100 (Low)
• Liquidity: Locked ✅
• Top holders: 15% concentration
• Copycat risk: None detected
Overall: Lower risk, but DYOR"
```

### Market Overview
```
User: "how's the market"
Response: "📊 Market Overview
Crypto: BTC $43.2K (+2%), ETH $2,290 (+1.8%)
Fear & Greed: 72 (Greed)
Trending: SOL, ONDO, WIF
Stocks: S&P +0.3%, NASDAQ +0.5%"
```

---

Built by [@NextXFrontier](https://x.com/NextXFrontier)
