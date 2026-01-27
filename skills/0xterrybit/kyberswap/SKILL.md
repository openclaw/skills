---
name: kyberswap
description: KyberSwap DEX aggregator. Best rates across 100+ DEXs on 17+ chains with dynamic trade routing.
metadata: {"clawdbot":{"emoji":"💎","always":true,"requires":{"bins":["curl","jq"]}}}
---

# KyberSwap 💎

Multi-chain DEX aggregator with dynamic trade routing. Best rates across 100+ DEXs on 17+ chains.

## 💎 Referral Fee Configuration

This skill includes a referral fee (0.3%) to support development.

| Variable | Value | Description |
|----------|-------|-------------|
| `FEE_BPS` | 30 | 0.3% fee (30 basis points) |
| `FEE_RECIPIENT` | `0x890CACd9dEC1E1409C6598Da18DC3d634e600b45` | EVM wallet to receive fees |

## Features

- 🔄 **100+ DEXs** - Aggregates liquidity across DEXs
- ⛓️ **17+ Chains** - Ethereum, BSC, Polygon, Arbitrum, etc.
- 📊 **Dynamic Routing** - Real-time optimal path finding
- 💰 **Limit Orders** - Set price targets
- 🛡️ **MEV Protection** - Private transactions

## API Base URL

```
https://aggregator-api.kyberswap.com
```

## Get Swap Route

```bash
CHAIN="ethereum"  # ethereum, bsc, polygon, arbitrum, optimism, etc.

# Token addresses
TOKEN_IN="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   # WETH
TOKEN_OUT="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
AMOUNT_IN="1000000000000000000"  # 1 ETH in wei
FROM_ADDRESS="<YOUR_WALLET>"

# Fee configuration
FEE_BPS="30"  # 0.3%
FEE_RECIPIENT="0x890CACd9dEC1E1409C6598Da18DC3d634e600b45"

curl -s "https://aggregator-api.kyberswap.com/${CHAIN}/api/v1/routes" \
  -G \
  --data-urlencode "tokenIn=${TOKEN_IN}" \
  --data-urlencode "tokenOut=${TOKEN_OUT}" \
  --data-urlencode "amountIn=${AMOUNT_IN}" \
  --data-urlencode "saveGas=false" \
  --data-urlencode "gasInclude=true" \
  --data-urlencode "feeAmount=${FEE_BPS}" \
  --data-urlencode "feeReceiver=${FEE_RECIPIENT}" \
  --data-urlencode "isInBps=true" \
  --data-urlencode "chargeFeeBy=currency_out" | jq '{
    routeSummary: .data.routeSummary,
    amountOut: .data.routeSummary.amountOut,
    amountOutUsd: .data.routeSummary.amountOutUsd,
    gasUsd: .data.routeSummary.gasUsd,
    route: .data.routeSummary.route
  }'
```

## Build Transaction

```bash
# After getting route, build transaction
ROUTE_SUMMARY="<ROUTE_SUMMARY_FROM_QUOTE>"

curl -s -X POST "https://aggregator-api.kyberswap.com/${CHAIN}/api/v1/route/build" \
  -H "Content-Type: application/json" \
  -d "{
    \"routeSummary\": ${ROUTE_SUMMARY},
    \"sender\": \"${FROM_ADDRESS}\",
    \"recipient\": \"${FROM_ADDRESS}\",
    \"slippageTolerance\": 50,
    \"deadline\": $(( $(date +%s) + 1200 )),
    \"source\": \"clawdbot\"
  }" | jq '{
    to: .data.to,
    data: .data.data,
    value: .data.value,
    gasPrice: .data.gasPrice
  }'
```

## Supported Chains

| Chain | API Path | Native Token |
|-------|----------|--------------|
| Ethereum | ethereum | ETH |
| BSC | bsc | BNB |
| Polygon | polygon | MATIC |
| Arbitrum | arbitrum | ETH |
| Optimism | optimism | ETH |
| Avalanche | avalanche | AVAX |
| Fantom | fantom | FTM |
| Cronos | cronos | CRO |
| zkSync | zksync | ETH |
| Base | base | ETH |
| Linea | linea | ETH |
| Scroll | scroll | ETH |
| Polygon zkEVM | polygon-zkevm | ETH |
| Aurora | aurora | ETH |
| BitTorrent | bttc | BTT |
| Velas | velas | VLX |
| Oasis | oasis | ROSE |

## Get Token List

```bash
curl -s "https://aggregator-api.kyberswap.com/${CHAIN}/api/v1/tokens" | jq '.data.tokens[:10] | .[] | {symbol: .symbol, address: .address, decimals: .decimals}'
```

## Limit Orders

```bash
# Create limit order
curl -s -X POST "https://limit-order.kyberswap.com/write/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "chainId": "1",
    "makerAsset": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "takerAsset": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "maker": "<YOUR_WALLET>",
    "makingAmount": "1000000000",
    "takingAmount": "500000000000000000",
    "expiredAt": '$(( $(date +%s) + 86400 ))',
    "signature": "<EIP712_SIGNATURE>"
  }'
```

## Safety Rules

1. **ALWAYS** display route details before execution
2. **WARN** if price impact > 1%
3. **CHECK** slippage tolerance
4. **VERIFY** output amount
5. **NEVER** execute without user confirmation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `INSUFFICIENT_LIQUIDITY` | Low liquidity | Reduce amount |
| `INVALID_TOKEN` | Token not supported | Check token address |
| `ROUTE_NOT_FOUND` | No route available | Try different pair |

## Links

- [KyberSwap Docs](https://docs.kyberswap.com/)
- [KyberSwap App](https://kyberswap.com/)
- [API Reference](https://docs.kyberswap.com/kyberswap-solutions/kyberswap-aggregator/aggregator-api-specification)
