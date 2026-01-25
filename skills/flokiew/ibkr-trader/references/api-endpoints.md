# IBKR Client Portal API Reference

Base URL: `https://localhost:5000`

All requests use HTTPS with self-signed certs (use `verify=False` or `-k` with curl).

## Authentication

### Check Status
```
GET /v1/api/iserver/auth/status
```
Response:
```json
{
  "authenticated": true,
  "competing": false,
  "connected": true,
  "message": "",
  "MAC": "...",
  "serverInfo": {...}
}
```

### Keepalive (Tickle)
```
POST /v1/api/tickle
```
Call every 5 minutes to keep session alive.

### Re-authenticate
```
POST /v1/portal/iserver/reauthenticate?force=true
```
Triggers re-authentication flow.

### Logout
```
POST /v1/api/logout
```

## Portfolio

### List Accounts
```
GET /v1/api/portfolio/accounts
```
Response:
```json
[{
  "id": "U1234567",
  "accountId": "U1234567",
  "accountTitle": "John Doe",
  "currency": "USD",
  "type": "INDIVIDUAL"
}]
```

### Account Summary
```
GET /v1/api/portfolio/{accountId}/summary
```
Key fields:
- `totalcashvalue.amount` - Available cash
- `netliquidation.amount` - Total account value
- `unrealizedpnl.amount` - Unrealized P&L

### Account Ledger
```
GET /v1/api/portfolio/{accountId}/ledger
```
Detailed breakdown by currency.

## Positions

### Get Positions
```
GET /v1/api/portfolio/{accountId}/positions/{pageId}
```
`pageId` starts at 0. Returns up to 30 positions per page.

Response:
```json
[{
  "acctId": "U1234567",
  "conid": 265598,
  "contractDesc": "AAPL",
  "position": 100,
  "mktPrice": 175.50,
  "mktValue": 17550,
  "avgCost": 150.00,
  "avgPrice": 150.00,
  "unrealizedPnl": 2550,
  "realizedPnl": 0
}]
```

### Position by Conid
```
GET /v1/api/portfolio/{accountId}/position/{conid}
```

## Market Data

### Symbol Search
```
GET /v1/api/iserver/secdef/search?symbol={symbol}
```
Response:
```json
[{
  "conid": 265598,
  "companyHeader": "APPLE INC",
  "companyName": "APPLE INC",
  "symbol": "AAPL",
  "description": "NASDAQ",
  "sections": [...]
}]
```

### Contract Details
```
GET /v1/api/iserver/contract/{conid}/info
```

### Market Data Snapshot
```
GET /v1/api/iserver/marketdata/snapshot?conids={conid}&fields={fields}
```

**Common Fields:**
| Field | Description |
|-------|-------------|
| 31 | Last Price |
| 84 | Bid Price |
| 86 | Ask Price |
| 87 | Volume |
| 88 | Previous Close |
| 7295 | Open Price |
| 7296 | High Price |
| 7297 | Low Price |
| 7762 | Change % |

Example:
```bash
curl -sk "https://localhost:5000/v1/api/iserver/marketdata/snapshot?conids=265598&fields=31,84,86,87"
```

### Historical Data
```
GET /v1/api/iserver/marketdata/history?conid={conid}&period={period}&bar={bar}
```

Periods: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`
Bars: `1min`, `5min`, `1h`, `1d`, `1w`, `1m`

## Orders

### Place Order
```
POST /v1/api/iserver/account/{accountId}/orders
Content-Type: application/json

{
  "orders": [{
    "conid": 265598,
    "orderType": "MKT",
    "side": "BUY",
    "quantity": 10,
    "tif": "DAY"
  }]
}
```

**Order Types:**
- `MKT` - Market order
- `LMT` - Limit order (requires `price`)
- `STP` - Stop order (requires `auxPrice`)
- `STP_LIMIT` - Stop limit (requires both)

**Time in Force (tif):**
- `DAY` - Day order
- `GTC` - Good till cancelled
- `IOC` - Immediate or cancel
- `OPG` - At the open

**Limit Order Example:**
```json
{
  "orders": [{
    "conid": 265598,
    "orderType": "LMT",
    "side": "BUY",
    "quantity": 10,
    "price": 170.00,
    "tif": "GTC"
  }]
}
```

### Confirm Order
After placing an order, you may receive a confirmation request:
```
POST /v1/api/iserver/reply/{replyId}
Content-Type: application/json

{"confirmed": true}
```

### Get Orders
```
GET /v1/api/iserver/account/orders
```

### Cancel Order
```
DELETE /v1/api/iserver/account/{accountId}/order/{orderId}
```

### Modify Order
```
POST /v1/api/iserver/account/{accountId}/order/{orderId}
Content-Type: application/json

{
  "conid": 265598,
  "orderType": "LMT",
  "price": 175.00,
  "quantity": 10,
  "side": "BUY",
  "tif": "DAY"
}
```

## Alerts

### Get Alerts
```
GET /v1/api/iserver/account/{accountId}/alerts
```

### Create Alert
```
POST /v1/api/iserver/account/{accountId}/alert
Content-Type: application/json

{
  "alertName": "AAPL Above 180",
  "alertMessage": "AAPL hit target",
  "outsideRth": 1,
  "conditions": [{
    "conidex": "265598@NASDAQ",
    "operator": ">=",
    "triggerMethod": "0",
    "value": "180"
  }]
}
```

## Scanner

### Get Scanner Parameters
```
GET /v1/api/iserver/scanner/params
```

### Run Scanner
```
POST /v1/api/iserver/scanner/run
Content-Type: application/json

{
  "instrument": "STK",
  "type": "TOP_PERC_GAIN",
  "location": "STK.US.MAJOR",
  "size": "25"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Not authenticated |
| 500 | Internal server error (often auth issue) |
| 503 | Gateway not ready |

## Rate Limits

- Market data: ~100 requests/second
- Orders: ~50 requests/second
- Portfolio: ~10 requests/second

Keep requests reasonable to avoid being throttled.
