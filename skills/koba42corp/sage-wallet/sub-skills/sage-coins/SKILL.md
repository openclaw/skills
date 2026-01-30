---
name: sage-coins
description: Sage coin and address operations. List coins, check spendability, validate addresses, get derivations, check asset ownership.
---

# Sage Coins & Addresses

Coin queries and address management.

## Endpoints

### Coin Queries

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_coins` | See below | List coins with filters |
| `get_coins_by_ids` | `{"coin_ids": [...]}` | Get specific coins |
| `get_are_coins_spendable` | `{"coin_ids": [...]}` | Check spendability |
| `get_spendable_coin_count` | `{"asset_id": null}` | Count spendable |

#### get_coins Payload

```json
{
  "asset_id": null,
  "offset": 0,
  "limit": 50,
  "sort_mode": "created_height",
  "filter_mode": "selectable",
  "ascending": false
}
```

Sort modes: `"coin_id"`, `"amount"`, `"created_height"`, `"spent_height"`, `"clawback_timestamp"`

Filter modes: `"all"`, `"selectable"`, `"owned"`, `"spent"`, `"clawback"`

### Address Operations

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `check_address` | `{"address": "xch1..."}` | Validate address |
| `get_derivations` | `{"hardened": false, "offset": 0, "limit": 50}` | Get derivations |
| `increase_derivation_index` | `{"index": 100, "hardened": true, "unhardened": true}` | Generate more |

### Asset Ownership

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `is_asset_owned` | `{"asset_id": "..."}` | Check if owned |

## Coin Record Structure

```json
{
  "coin_id": "0x...",
  "parent_coin_info": "0x...",
  "puzzle_hash": "0x...",
  "amount": "1000000000000",
  "asset_id": null,
  "created_height": 1234567,
  "spent_height": null,
  "clawback_timestamp": null
}
```

## Derivation Record Structure

```json
{
  "index": 0,
  "hardened": false,
  "address": "xch1...",
  "puzzle_hash": "0x...",
  "public_key": "0x..."
}
```

## Examples

```bash
# List XCH coins
sage_rpc get_coins '{"asset_id": null, "limit": 20}'

# List CAT coins
sage_rpc get_coins '{"asset_id": "a628c1c2...", "limit": 20}'

# Check address
sage_rpc check_address '{"address": "xch1abc..."}'

# Check if coins are spendable
sage_rpc get_are_coins_spendable '{"coin_ids": ["0xabc...", "0xdef..."]}'

# Get address derivations
sage_rpc get_derivations '{"hardened": false, "offset": 0, "limit": 10}'

# Generate more addresses
sage_rpc increase_derivation_index '{"index": 200, "hardened": true, "unhardened": true}'
```

## Notes

- `asset_id: null` queries XCH coins
- `filter_mode: "selectable"` returns only spendable coins
- Address validation checks format and wallet ownership
