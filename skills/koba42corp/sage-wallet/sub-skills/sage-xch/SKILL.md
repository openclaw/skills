---
name: sage-xch
description: Sage XCH transaction operations. Send XCH, bulk send, combine coins, split coins, multi-send, clawback finalization.
---

# Sage XCH Transactions

XCH (Chia) transaction operations.

## Amount Format

All amounts in mojos (string): `1 XCH = "1000000000000"`

## Endpoints

### Send XCH

| Endpoint | Description |
|----------|-------------|
| `send_xch` | Send to single address |
| `bulk_send_xch` | Send to multiple addresses |
| `multi_send` | Send multiple asset types |

#### send_xch

```json
{
  "address": "xch1...",
  "amount": "1000000000000",
  "fee": "100000000",
  "memos": ["optional memo"],
  "clawback": null,
  "auto_submit": true
}
```

#### bulk_send_xch

```json
{
  "addresses": ["xch1...", "xch1..."],
  "amount": "100000000000",
  "fee": "100000000",
  "memos": [],
  "auto_submit": true
}
```

#### multi_send

```json
{
  "payments": [
    {"asset_id": null, "address": "xch1...", "amount": "1000000000000", "memos": []},
    {"asset_id": "a628c1c2...", "address": "xch1...", "amount": "1000", "memos": []}
  ],
  "fee": "100000000",
  "auto_submit": true
}
```

### Coin Management

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `combine` | `{"coin_ids": [...], "fee": "...", "auto_submit": true}` | Merge coins |
| `split` | `{"coin_ids": [...], "output_count": 10, "fee": "...", "auto_submit": true}` | Split coin |
| `auto_combine_xch` | See below | Auto-merge small coins |

#### auto_combine_xch

```json
{
  "max_coins": 500,
  "max_coin_amount": "1000000000000",
  "fee": "100000000",
  "auto_submit": true
}
```

### Clawback

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `finalize_clawback` | `{"coin_ids": [...], "fee": "...", "auto_submit": true}` | Complete clawback |

## Response Format

All transaction endpoints return:

```json
{
  "summary": {
    "fee": "100000000",
    "inputs": [...],
    "outputs": [...]
  },
  "coin_spends": [...]
}
```

## Examples

```bash
# Send 1 XCH
sage_rpc send_xch '{
  "address": "xch1abc...",
  "amount": "1000000000000",
  "fee": "100000000",
  "auto_submit": true
}'

# Combine dust
sage_rpc auto_combine_xch '{
  "max_coins": 100,
  "fee": "50000000",
  "auto_submit": true
}'
```

## Clawback Feature

Send with clawback (recoverable for N seconds):

```json
{
  "address": "xch1...",
  "amount": "1000000000000",
  "fee": "100000000",
  "clawback": 86400,
  "auto_submit": true
}
```

After clawback period, recipient runs `finalize_clawback` to claim.
