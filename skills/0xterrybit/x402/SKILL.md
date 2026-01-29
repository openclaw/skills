---
name: x402
description: Use x402 protocol for HTTP-native crypto payments. Use when Clawdbot needs to pay for APIs, access paid resources, or handle 402 Payment Required responses. Supports USDC payments on Base, Ethereum, and other EVM chains via the x402 standard.
metadata: {"clawdbot":{"emoji":"💸","requires":{"anyBins":["node","npx"]},"env":["WALLET_PRIVATE_KEY"]}}
---

# x402 Payment Protocol

x402 enables instant stablecoin payments directly over HTTP using the 402 Payment Required status code. Perfect for AI agents paying for APIs, data, or compute on-demand.

## Quick Start

### Install SDK
```bash
npm install x402
# or
pnpm add x402
```

### Environment Setup
```bash
# Store wallet private key securely
export WALLET_PRIVATE_KEY="0x..."

# Optional: specify network RPC
export BASE_RPC_URL="https://mainnet.base.org"
```

## How x402 Works

1. **Request** → Client calls a paid API
2. **402 Response** → Server returns payment details in `PAYMENT-REQUIRED` header
3. **Pay & Retry** → Client signs payment, retries with `PAYMENT-SIGNATURE` header
4. **Access** → Server verifies, settles, returns resource

## Using x402 Client

### TypeScript/Node.js
```typescript
import { x402Client } from 'x402';

const client = x402Client({
  privateKey: process.env.WALLET_PRIVATE_KEY,
  network: 'base', // or 'ethereum', 'arbitrum', etc.
});

// Automatic 402 handling
const response = await client.fetch('https://api.example.com/paid-endpoint');
const data = await response.json();
```

### With fetch wrapper
```typescript
import { wrapFetch } from 'x402';

const fetch402 = wrapFetch(fetch, {
  privateKey: process.env.WALLET_PRIVATE_KEY,
});

// Use like normal fetch - 402s handled automatically
const res = await fetch402('https://paid-api.com/data');
```

## Manual Flow (curl)

### Step 1: Discover payment requirements
```bash
curl -i https://api.example.com/paid-resource
# Returns 402 with PAYMENT-REQUIRED header (base64 JSON)
```

### Step 2: Decode payment details
```bash
# The PAYMENT-REQUIRED header contains base64-encoded JSON:
# {
#   "amount": "1000000",      # 1 USDC (6 decimals)
#   "currency": "USDC",
#   "network": "base",
#   "recipient": "0x...",
#   "scheme": "exact"
# }
```

### Step 3: Sign and pay
```bash
# Use x402 CLI or SDK to create payment signature
npx x402 pay \
  --amount 1000000 \
  --recipient 0x... \
  --network base
```

### Step 4: Retry with proof
```bash
curl -H "PAYMENT-SIGNATURE: <base64_payload>" \
  https://api.example.com/paid-resource
```

## Common Patterns

### Pay for API calls
```typescript
// Weather API that costs 0.001 USDC per call
const weather = await client.fetch('https://weather-api.x402.org/forecast?city=NYC');
```

### Pay for AI inference
```typescript
// LLM API with per-token pricing
const completion = await client.fetch('https://llm.example.com/v1/chat', {
  method: 'POST',
  body: JSON.stringify({ prompt: 'Hello' }),
});
```

### Check balance before paying
```typescript
import { getBalance } from 'x402';

const balance = await getBalance({
  address: walletAddress,
  network: 'base',
  token: 'USDC',
});

if (balance < requiredAmount) {
  console.log('Insufficient USDC balance');
}
```

## Supported Networks

| Network | Chain ID | Status |
|---------|----------|--------|
| Base | 8453 | ✅ Primary |
| Ethereum | 1 | ✅ Supported |
| Arbitrum | 42161 | ✅ Supported |
| Optimism | 10 | ✅ Supported |
| Polygon | 137 | ✅ Supported |

## Payment Schemes

- **exact**: Pay fixed amount (e.g., $0.01 per API call)
- **upto**: Pay up to max based on usage (e.g., LLM tokens)
- **subscription**: Wallet-based access with sessions (V2)

## Error Handling

```typescript
try {
  const res = await client.fetch(url);
} catch (err) {
  if (err.code === 'INSUFFICIENT_BALANCE') {
    // Need to fund wallet
  } else if (err.code === 'PAYMENT_FAILED') {
    // Transaction failed on-chain
  } else if (err.code === 'INVALID_PAYMENT_REQUIREMENTS') {
    // Server sent malformed 402 response
  }
}
```

## Security Notes

- Never expose private keys in logs or chat
- Use environment variables for wallet credentials
- Prefer `op run` or similar for secret injection
- Review payment amounts before confirming large transactions

## V2 Features (Dec 2025)

- **Wallet-based identity**: Skip repaying on every call with sessions
- **Auto-discovery**: APIs expose payment metadata at `/.well-known/x402`
- **Multi-facilitator**: Choose between payment processors
- **CAIP standards**: Universal chain/asset identifiers

## Resources

- Spec: https://github.com/coinbase/x402
- Docs: https://docs.cdp.coinbase.com/x402
- Demo APIs: https://www.x402.org
