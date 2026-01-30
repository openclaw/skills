---
name: sage-txn
description: Sage transaction operations. List transactions, sign coin spends, view without signing, submit transactions.
---

# Sage Transactions

Transaction signing and submission.

## Endpoints

### Query Transactions

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_transactions` | See below | List transactions |
| `get_transaction` | `{"height": 1234567}` | Get by height |
| `get_pending_transactions` | `{}` | List pending |

#### get_transactions Payload

```json
{
  "offset": 0,
  "limit": 50,
  "ascending": false,
  "find_value": null
}
```

### Sign & Submit

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `sign_coin_spends` | See below | Sign transaction |
| `view_coin_spends` | `{"coin_spends": [...]}` | Preview without signing |
| `submit_transaction` | `{"spend_bundle": {...}}` | Broadcast |

#### sign_coin_spends

```json
{
  "coin_spends": [
    {
      "coin": {
        "parent_coin_info": "0x...",
        "puzzle_hash": "0x...",
        "amount": 1000000000000
      },
      "puzzle_reveal": "0x...",
      "solution": "0x..."
    }
  ],
  "auto_submit": false,
  "partial": false
}
```

- `partial: true` for multi-sig partial signatures

#### submit_transaction

```json
{
  "spend_bundle": {
    "coin_spends": [...],
    "aggregated_signature": "0x..."
  }
}
```

## Transaction Record Structure

```json
{
  "height": 1234567,
  "timestamp": 1700000000,
  "fee": "100000000",
  "inputs": [...],
  "outputs": [...]
}
```

## Pending Transaction Structure

```json
{
  "transaction_id": "0x...",
  "fee": "100000000",
  "submitted_at": 1700000000,
  "coin_spends": [...]
}
```

## Examples

```bash
# List recent transactions
sage_rpc get_transactions '{"limit": 20, "ascending": false}'

# Get pending
sage_rpc get_pending_transactions '{}'

# View coin spends (preview)
sage_rpc view_coin_spends '{"coin_spends": [...]}'

# Sign and submit
sage_rpc sign_coin_spends '{
  "coin_spends": [...],
  "auto_submit": true
}'

# Manual submit
sage_rpc submit_transaction '{"spend_bundle": {...}}'
```

## Workflow

1. Build coin spends (from other endpoints with `auto_submit: false`)
2. Optionally `view_coin_spends` to preview
3. `sign_coin_spends` to create spend bundle
4. `submit_transaction` to broadcast (or use `auto_submit: true`)

## Notes

- `auto_submit: true` signs and broadcasts in one call
- `partial: true` for multi-signature workflows
- Pending transactions await mempool confirmation
