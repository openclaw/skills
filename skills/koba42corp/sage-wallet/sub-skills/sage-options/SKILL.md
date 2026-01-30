---
name: sage-options
description: Sage options protocol operations. Mint options, exercise, transfer, list and manage options contracts.
---

# Sage Options

Chia options protocol operations.

## Endpoints

### Query Options

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_options` | See below | List options |
| `get_option` | `{"option_id": "..."}` | Get specific option |
| `update_option` | `{"option_id": "...", "visible": true}` | Update visibility |

#### get_options Payload

```json
{
  "offset": 0,
  "limit": 50,
  "sort_mode": "name",
  "ascending": false,
  "find_value": null,
  "include_hidden": false
}
```

Sort modes: `"name"`, `"created_height"`, `"expiration_seconds"`

### Mint Option

```json
{
  "expiration_seconds": 604800,
  "underlying": {
    "asset_id": null,
    "amount": "1000000000000"
  },
  "strike": {
    "asset_id": "a628c1c2...",
    "amount": "100000"
  },
  "fee": "100000000",
  "auto_submit": true
}
```

- `asset_id: null` = XCH
- Returns `option_id`

### Exercise Options

```json
{
  "option_ids": ["..."],
  "fee": "100000000",
  "auto_submit": true
}
```

### Transfer Options

```json
{
  "option_ids": ["..."],
  "address": "xch1...",
  "fee": "100000000",
  "clawback": null,
  "auto_submit": true
}
```

## Option Record Structure

```json
{
  "option_id": "...",
  "underlying_asset_id": null,
  "underlying_amount": "1000000000000",
  "strike_asset_id": "a628c1c2...",
  "strike_amount": "100000",
  "expiration_seconds": 604800,
  "created_height": 1234567,
  "visible": true
}
```

## Examples

```bash
# List options
sage_rpc get_options '{"limit": 20}'

# Mint option: 1 XCH underlying, 100k CAT strike, 7 day expiry
sage_rpc mint_option '{
  "expiration_seconds": 604800,
  "underlying": {"asset_id": null, "amount": "1000000000000"},
  "strike": {"asset_id": "a628c1c2...", "amount": "100000"},
  "fee": "100000000",
  "auto_submit": true
}'

# Exercise option
sage_rpc exercise_options '{
  "option_ids": ["option123"],
  "fee": "100000000",
  "auto_submit": true
}'

# Transfer option
sage_rpc transfer_options '{
  "option_ids": ["option123"],
  "address": "xch1buyer...",
  "fee": "100000000",
  "auto_submit": true
}'
```

## Notes

- Options allow derivative-style contracts on Chia
- Exercise before expiration to claim underlying
- Expired options can be reclaimed by creator
