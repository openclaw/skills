---
name: sage-cat
description: Sage CAT (Chia Asset Token) operations. List tokens, send CATs, issue new tokens, combine CAT coins, resync balances.
---

# Sage CAT Tokens

CAT (Chia Asset Token) operations.

## Endpoints

### Query CATs

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_cats` | `{}` | List wallet CATs |
| `get_all_cats` | `{}` | List all known CATs |
| `get_token` | `{"asset_id": "a628..."}` | Get token details |

### Token Metadata

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `update_cat` | `{"record": {...}}` | Update CAT metadata |
| `resync_cat` | `{"asset_id": "a628..."}` | Resync CAT balance |

### Send CAT

| Endpoint | Description |
|----------|-------------|
| `send_cat` | Send to single address |
| `bulk_send_cat` | Send to multiple addresses |

#### send_cat

```json
{
  "asset_id": "a628c1c2c6fcb74d53746157e438e108eab5c0bb3e5c80ff9b1910b3e4832913",
  "address": "xch1...",
  "amount": "1000",
  "fee": "100000000",
  "include_hint": true,
  "memos": [],
  "clawback": null,
  "auto_submit": true
}
```

#### bulk_send_cat

```json
{
  "asset_id": "a628...",
  "addresses": ["xch1...", "xch1..."],
  "amount": "100",
  "fee": "100000000",
  "include_hint": true,
  "memos": [],
  "auto_submit": true
}
```

### Issue CAT

Create new token:

```json
{
  "name": "My Token",
  "ticker": "MYT",
  "amount": "1000000",
  "fee": "100000000",
  "auto_submit": true
}
```

### Combine CAT Coins

```json
{
  "asset_id": "a628...",
  "max_coins": 100,
  "max_coin_amount": "1000000",
  "fee": "100000000",
  "auto_submit": true
}
```

## Token Record Structure

```json
{
  "asset_id": "a628c1c2...",
  "name": "Spacebucks",
  "ticker": "SBX",
  "balance": "1000000",
  "icon_url": "https://...",
  "visible": true
}
```

## Examples

```bash
# List CATs
sage_rpc get_cats '{}'

# Send CAT
sage_rpc send_cat '{
  "asset_id": "a628c1c2c6fcb74d53746157e438e108eab5c0bb3e5c80ff9b1910b3e4832913",
  "address": "xch1recipient...",
  "amount": "100",
  "fee": "100000000",
  "auto_submit": true
}'

# Issue new token
sage_rpc issue_cat '{
  "name": "Community Token",
  "ticker": "COM",
  "amount": "21000000",
  "fee": "100000000",
  "auto_submit": true
}'
```

## Notes

- CAT amounts are in the token's smallest unit (no decimals)
- `include_hint` adds the asset_id to help receivers identify the token
- Asset IDs are 64-character hex strings
