# x402 Protocol Specification Reference

## Headers

### Request Headers

| Header | Description |
|--------|-------------|
| `PAYMENT-SIGNATURE` | Base64-encoded payment payload with signature |

### Response Headers

| Header | Status | Description |
|--------|--------|-------------|
| `PAYMENT-REQUIRED` | 402 | Base64-encoded payment requirements |
| `PAYMENT-RESPONSE` | 200 | Base64-encoded settlement confirmation |

## Payment Requirements Schema

```typescript
interface PaymentRequirement {
  // Amount in smallest unit (e.g., 1000000 = 1 USDC)
  amount: string;
  
  // Token symbol
  currency: 'USDC' | 'USDT' | 'DAI';
  
  // Network identifier (CAIP-2 in V2)
  network: 'base' | 'ethereum' | 'arbitrum' | 'optimism' | 'polygon';
  
  // Recipient address
  recipient: string;
  
  // Payment scheme
  scheme: 'exact' | 'upto';
  
  // Optional facilitator URL
  facilitator?: string;
  
  // V2: Additional metadata
  metadata?: {
    description?: string;
    expiry?: number;
    nonce?: string;
  };
}
```

## Payment Payload Schema

```typescript
interface PaymentPayload {
  // EIP-712 signature
  signature: string;
  
  // Sender wallet address
  sender: string;
  
  // Unique nonce (timestamp or random)
  nonce: number;
  
  // Network used for payment
  network: string;
  
  // Scheme used
  scheme: string;
  
  // V2: Optional authorization token for sessions
  authorization?: string;
}
```

## Settlement Response Schema

```typescript
interface SettlementResponse {
  // Transaction hash (if on-chain)
  txHash?: string;
  
  // Settlement status
  status: 'settled' | 'pending' | 'failed';
  
  // Block number
  blockNumber?: number;
  
  // Timestamp
  timestamp: number;
}
```

## Schemes

### exact
Fixed payment amount. Client pays exactly what's specified.

```json
{
  "scheme": "exact",
  "amount": "1000000",
  "currency": "USDC"
}
```

### upto (V2)
Maximum payment amount. Actual charge based on usage.

```json
{
  "scheme": "upto",
  "maxAmount": "10000000",
  "currency": "USDC",
  "pricePerUnit": "1000",
  "unit": "token"
}
```

## EIP-712 Domain

```typescript
const domain = {
  name: 'x402',
  version: '2',
  chainId: 8453, // Base mainnet
};

const types = {
  Payment: [
    { name: 'recipient', type: 'address' },
    { name: 'amount', type: 'uint256' },
    { name: 'token', type: 'address' },
    { name: 'nonce', type: 'uint256' },
  ],
};
```

## V2 Discovery Extension

Services can expose metadata at `/.well-known/x402`:

```json
{
  "version": "2.0",
  "endpoints": [
    {
      "path": "/api/v1/*",
      "pricing": {
        "scheme": "exact",
        "amount": "1000",
        "currency": "USDC"
      }
    }
  ],
  "networks": ["base", "ethereum"],
  "facilitators": ["https://facilitator.coinbase.com"]
}
```

## V2 Session-Based Access

Using wallet signatures for reusable sessions:

```typescript
// 1. Sign-in request
POST /auth/x402
{
  "wallet": "0x...",
  "signature": "<SIWE signature>",
  "message": "<CAIP-122 message>"
}

// 2. Receive session token
{
  "token": "eyJ...",
  "expiresAt": 1735689600
}

// 3. Use token for subsequent requests
GET /api/resource
Authorization: Bearer eyJ...
```

## Error Codes

| Code | Meaning |
|------|---------|
| `INSUFFICIENT_BALANCE` | Wallet lacks funds |
| `INVALID_SIGNATURE` | Payment signature invalid |
| `EXPIRED_PAYMENT` | Payment nonce/timestamp expired |
| `UNSUPPORTED_NETWORK` | Server doesn't accept this network |
| `SETTLEMENT_FAILED` | On-chain transaction failed |
| `FACILITATOR_ERROR` | Facilitator service unavailable |

## Facilitator Endpoints

### POST /verify
Verify payment signature without settling.

### POST /settle
Verify and execute on-chain settlement.

### GET /status/:txHash
Check settlement status.
