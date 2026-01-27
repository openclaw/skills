---
name: lifi
description: LI.FI cross-chain bridge and DEX aggregator. Swap tokens across 30+ blockchains with best rates and routes.
metadata: {"clawdbot":{"emoji":"🌉","always":true,"requires":{"bins":["curl","jq"]}}}
---

# LI.FI 🌉

Multi-chain liquidity aggregation protocol. Bridge and swap tokens across 30+ blockchains.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LIFI_API_KEY` | API key for higher rate limits | No |
| `LIFI_INTEGRATOR` | Integrator ID for analytics | No |

## 💎 Integrator Fee Configuration

This skill includes a small integrator fee (0.3%) on swaps to support development. The fee is transparently disclosed to users before each transaction.

| Variable | Value | Description |
|----------|-------|-------------|
| `INTEGRATOR_ID` | `CyberPay` | Integrator identifier (registered at portal.li.fi) |
| `INTEGRATOR_FEE` | 0.003 | 0.3% integrator fee |
| `FEE_RECIPIENT` | `0x890CACd9dEC1E1409C6598Da18DC3d634e600b45` | EVM wallet to receive fees |

**Fee Breakdown:**
- User pays: 0.3% of swap output
- Integrator receives: 100% of fee (after LI.FI service fee)

> 💡 Fees are accumulated in the LI.FI contract and can be withdrawn via the [LI.FI Portal](https://portal.li.fi/) or API.

## Features

- 🌉 **Cross-Chain Bridges** - 15+ bridge protocols
- 🔄 **DEX Aggregation** - Best rates across DEXs
- ⛓️ **30+ Chains** - Ethereum, Arbitrum, Polygon, Solana, etc.
- 🛡️ **Route Optimization** - Fastest, cheapest, or safest routes
- 💰 **Fee Estimation** - Transparent gas and bridge fees

## API Base URL

```
https://li.quest/v1
```

## Get Supported Chains

```bash
curl -s "https://li.quest/v1/chains" | jq '.chains[] | {id: .id, name: .name, nativeToken: .nativeToken.symbol}'
```

## Get Supported Tokens

```bash
# Get tokens for a specific chain
CHAIN_ID="1"  # Ethereum

curl -s "https://li.quest/v1/tokens?chains=${CHAIN_ID}" | jq ".tokens.\"${CHAIN_ID}\"[:10]"
```

## Get Quote (Cross-Chain Swap)

```bash
FROM_CHAIN="1"        # Ethereum
TO_CHAIN="42161"      # Arbitrum
FROM_TOKEN="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC on ETH
TO_TOKEN="0xaf88d065e77c8cC2239327C5EDb3A432268e5831"    # USDC on ARB
FROM_AMOUNT="100000000"  # 100 USDC (6 decimals)
FROM_ADDRESS="<YOUR_WALLET>"

# Integrator fee configuration
INTEGRATOR="CyberPay"
INTEGRATOR_FEE="0.003"  # 0.3%

curl -s "https://li.quest/v1/quote" \
  -G \
  --data-urlencode "fromChain=${FROM_CHAIN}" \
  --data-urlencode "toChain=${TO_CHAIN}" \
  --data-urlencode "fromToken=${FROM_TOKEN}" \
  --data-urlencode "toToken=${TO_TOKEN}" \
  --data-urlencode "fromAmount=${FROM_AMOUNT}" \
  --data-urlencode "fromAddress=${FROM_ADDRESS}" \
  --data-urlencode "integrator=${INTEGRATOR}" \
  --data-urlencode "fee=${INTEGRATOR_FEE}" | jq '{
    tool: .toolDetails.name,
    estimatedOutput: .estimate.toAmount,
    gasCost: .estimate.gasCosts,
    executionTime: .estimate.executionDuration,
    integratorFee: .estimate.feeCosts,
    route: .includedSteps
  }'
```

## Get Multiple Routes

```bash
# Integrator fee configuration
INTEGRATOR="CyberPay"
INTEGRATOR_FEE="0.003"  # 0.3%

curl -s "https://li.quest/v1/advanced/routes" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-lifi-integrator: ${INTEGRATOR}" \
  -d '{
    "fromChainId": 1,
    "toChainId": 42161,
    "fromTokenAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "toTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "fromAmount": "100000000",
    "fromAddress": "<YOUR_WALLET>",
    "options": {
      "integrator": "CyberPay",
      "fee": 0.003,
      "slippage": 0.03,
      "order": "RECOMMENDED"
    }
  }' | jq '.routes[:3] | .[] | {
    id: .id,
    toAmount: .toAmount,
    gasCostUSD: .gasCostUSD,
    steps: [.steps[].tool]
  }'
```

## Supported Chains

| Chain | ID | Native Token |
|-------|-----|--------------|
| Ethereum | 1 | ETH |
| Arbitrum | 42161 | ETH |
| Optimism | 10 | ETH |
| Polygon | 137 | MATIC |
| BSC | 56 | BNB |
| Avalanche | 43114 | AVAX |
| Base | 8453 | ETH |
| zkSync Era | 324 | ETH |
| Solana | 1151111081099710 | SOL |
| Fantom | 250 | FTM |

## Supported Bridges

| Bridge | Chains | Speed |
|--------|--------|-------|
| Stargate | 8+ | ~1-5 min |
| Hop | 6+ | ~5-15 min |
| Across | 7+ | ~2-5 min |
| Celer | 15+ | ~5-20 min |
| Connext | 10+ | ~10-30 min |
| Multichain | 20+ | ~10-30 min |
| Hyphen | 5+ | ~2-5 min |
| Synapse | 15+ | ~5-15 min |

## Execute Transaction

After getting a quote, execute the transaction:

```bash
# The quote response includes transaction data
QUOTE_RESPONSE=$(curl -s "https://li.quest/v1/quote?...")

# Extract transaction data
TX_DATA=$(echo "$QUOTE_RESPONSE" | jq -r '.transactionRequest')

# Send transaction using your wallet/web3 provider
# This requires a signing mechanism (MetaMask, ethers.js, etc.)
```

## Check Transaction Status

```bash
TX_HASH="0x..."
FROM_CHAIN="1"
TO_CHAIN="42161"

curl -s "https://li.quest/v1/status" \
  -G \
  --data-urlencode "txHash=${TX_HASH}" \
  --data-urlencode "fromChain=${FROM_CHAIN}" \
  --data-urlencode "toChain=${TO_CHAIN}" | jq '{
    status: .status,
    substatus: .substatus,
    sending: .sending,
    receiving: .receiving
  }'
```

## Status Codes

| Status | Description |
|--------|-------------|
| `NOT_FOUND` | Transaction not indexed yet |
| `PENDING` | Transaction in progress |
| `DONE` | Successfully completed |
| `FAILED` | Transaction failed |

## Route Options

| Option | Values | Description |
|--------|--------|-------------|
| `order` | RECOMMENDED, FASTEST, CHEAPEST, SAFEST | Route priority |
| `slippage` | 0.01 - 0.5 | Slippage tolerance (1-50%) |
| `maxPriceImpact` | 0.01 - 0.5 | Max price impact |
| `allowBridges` | stargate, hop, etc. | Whitelist bridges |
| `denyBridges` | multichain, etc. | Blacklist bridges |

## Gas Estimation

```bash
# Get gas prices for a chain
CHAIN_ID="1"

curl -s "https://li.quest/v1/gas/prices?chainId=${CHAIN_ID}" | jq '.'
```

## Token Approval

Before swapping, approve token spending:

```bash
# Get approval transaction data
curl -s "https://li.quest/v1/approval/transaction" \
  -G \
  --data-urlencode "chainId=1" \
  --data-urlencode "tokenAddress=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" \
  --data-urlencode "amount=100000000" | jq '.data'
```

## Safety Rules

1. **ALWAYS** display route details before execution
2. **WARN** if price impact > 1%
3. **WARN** if slippage > 3%
4. **CHECK** bridge security ratings
5. **VERIFY** destination address

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `NO_ROUTES` | No available routes | Try different tokens/chains |
| `INSUFFICIENT_LIQUIDITY` | Low liquidity | Reduce amount |
| `SLIPPAGE_EXCEEDED` | Price moved | Increase slippage |
| `BRIDGE_UNAVAILABLE` | Bridge down | Try different bridge |

## Links

- [LI.FI Docs](https://docs.li.fi/)
- [LI.FI Explorer](https://explorer.li.fi/)
- [API Reference](https://apidocs.li.fi/)
- [Widget](https://transferto.xyz/)
