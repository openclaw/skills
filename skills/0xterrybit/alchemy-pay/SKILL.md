---
name: alchemy-pay
description: Alchemy Pay (ACH) fiat-to-crypto payment gateway integration. On-ramp, off-ramp, merchant payments, and NFT checkout services.
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["curl","jq"],"env":["ALCHEMY_PAY_APP_ID","ALCHEMY_PAY_SECRET"]}}}
---

# Alchemy Pay 💎

Hybrid payment infrastructure connecting crypto and traditional finance. Integrated with Binance Pay, Solana Pay, and 300+ payment channels worldwide.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ALCHEMY_PAY_APP_ID` | Merchant App ID | Yes |
| `ALCHEMY_PAY_SECRET` | API Secret Key | Yes |
| `ALCHEMY_PAY_ENV` | Environment: `sandbox` or `production` | No (default: sandbox) |

## Features

- 🔄 **On-Ramp** - Buy crypto with fiat (170+ countries)
- 💸 **Off-Ramp** - Sell crypto to fiat
- 🛒 **Merchant Payments** - Accept crypto payments
- 🎨 **NFT Checkout** - Fiat-to-NFT purchases
- 🌍 **Global Coverage** - Strong in Asia & LATAM

## API Endpoints

### Base URLs
- Sandbox: `https://openapi-test.alchemypay.org`
- Production: `https://openapi.alchemypay.org`

### Create On-Ramp Order

```bash
APP_ID="${ALCHEMY_PAY_APP_ID}"
SECRET="${ALCHEMY_PAY_SECRET}"
BASE_URL="${ALCHEMY_PAY_ENV:-sandbox}"
[[ "$BASE_URL" == "production" ]] && BASE_URL="https://openapi.alchemypay.org" || BASE_URL="https://openapi-test.alchemypay.org"

TIMESTAMP=$(date +%s)
NONCE=$(openssl rand -hex 16)

# Create signature
SIGN_STRING="appId=${APP_ID}&nonce=${NONCE}&timestamp=${TIMESTAMP}"
SIGNATURE=$(echo -n "${SIGN_STRING}${SECRET}" | sha256sum | cut -d' ' -f1)

curl -s -X POST "${BASE_URL}/open/api/v4/merchant/order/create" \
  -H "Content-Type: application/json" \
  -H "appId: ${APP_ID}" \
  -H "timestamp: ${TIMESTAMP}" \
  -H "nonce: ${NONCE}" \
  -H "sign: ${SIGNATURE}" \
  -d '{
    "crypto": "USDT",
    "network": "ETH",
    "fiat": "USD",
    "fiatAmount": "100",
    "walletAddress": "<USER_WALLET>",
    "callbackUrl": "https://your-callback.com/webhook"
  }' | jq '.'
```

### Get Supported Cryptocurrencies

```bash
curl -s "${BASE_URL}/open/api/v4/merchant/crypto/list" \
  -H "appId: ${APP_ID}" \
  -H "timestamp: ${TIMESTAMP}" \
  -H "nonce: ${NONCE}" \
  -H "sign: ${SIGNATURE}" | jq '.data'
```

### Get Exchange Rate

```bash
curl -s "${BASE_URL}/open/api/v4/merchant/price" \
  -H "appId: ${APP_ID}" \
  -H "timestamp: ${TIMESTAMP}" \
  -H "nonce: ${NONCE}" \
  -H "sign: ${SIGNATURE}" \
  -G --data-urlencode "crypto=BTC" \
     --data-urlencode "fiat=USD" | jq '.data'
```

### Check Order Status

```bash
ORDER_ID="<ORDER_ID>"

curl -s "${BASE_URL}/open/api/v4/merchant/order/query" \
  -H "appId: ${APP_ID}" \
  -H "timestamp: ${TIMESTAMP}" \
  -H "nonce: ${NONCE}" \
  -H "sign: ${SIGNATURE}" \
  -G --data-urlencode "orderId=${ORDER_ID}" | jq '.'
```

## Supported Payment Methods

| Region | Methods |
|--------|---------|
| Global | Visa, Mastercard, Apple Pay, Google Pay |
| Asia | Alipay, WeChat Pay, GrabPay, GCash |
| LATAM | PIX, SPEI, PSE |
| Europe | SEPA, iDEAL, Bancontact |

## Supported Cryptocurrencies

- **EVM**: ETH, USDT, USDC, BNB, MATIC
- **Solana**: SOL, USDC-SPL
- **Bitcoin**: BTC
- **Others**: TRX, AVAX, ARB

## Widget Integration

```html
<!-- Embed Alchemy Pay widget -->
<iframe 
  src="https://ramp.alchemypay.org?appId=YOUR_APP_ID&crypto=ETH&network=ETH&fiat=USD"
  width="400" 
  height="600"
  frameborder="0">
</iframe>
```

## Webhook Events

| Event | Description |
|-------|-------------|
| `PAY_SUCCESS` | Payment completed |
| `PAY_FAIL` | Payment failed |
| `REFUND_SUCCESS` | Refund processed |

## Safety Rules

1. **ALWAYS** verify webhook signatures
2. **NEVER** expose API secrets in client-side code
3. **ALWAYS** use HTTPS for callbacks
4. **VERIFY** order amounts match expected values

## Error Codes

| Code | Description |
|------|-------------|
| 10001 | Invalid signature |
| 10002 | Invalid parameters |
| 10003 | Order not found |
| 20001 | Insufficient balance |

## Links

- [Alchemy Pay Docs](https://alchemypay.readme.io/)
- [Dashboard](https://dashboard.alchemypay.org/)
- [Status Page](https://status.alchemypay.org/)
