---
name: sage-walletconnect
description: Sage WalletConnect integration. Filter coins, get asset coins, sign messages, send transactions for dApp connectivity.
---

# Sage WalletConnect

WalletConnect protocol integration for dApp connectivity.

## Endpoints

### Coin Operations

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `filter_unlocked_coins` | `{"coin_ids": [...]}` | Filter to unlocked |
| `get_asset_coins` | See below | Get spendable coins |

#### get_asset_coins Payload

```json
{
  "type": "cat",
  "asset_id": "a628c1c2...",
  "included_locked": false,
  "offset": 0,
  "limit": 50
}
```

Asset types: `"cat"`, `"did"`, `"nft"`

### Message Signing

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `sign_message_with_public_key` | `{"message": "...", "public_key": "0x..."}` | Sign with pubkey |
| `sign_message_by_address` | `{"message": "...", "address": "xch1..."}` | Sign with address key |

### Transaction

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `send_transaction_immediately` | `{"spend_bundle": {...}}` | Direct broadcast |

## Spendable Coin Structure

```json
{
  "coin": {
    "parent_coin_info": "0x...",
    "puzzle_hash": "0x...",
    "amount": 1000000000000
  },
  "coin_name": "0x...",
  "puzzle": "0x...",
  "confirmed_block_index": 1234567,
  "locked": false,
  "lineage_proof": {
    "parent_name": "0x...",
    "inner_puzzle_hash": "0x...",
    "amount": 1000
  }
}
```

## Sign Message Response

```json
{
  "public_key": "0x...",
  "signature": "0x..."
}
```

## Send Transaction Response

```json
{
  "status": 1,
  "error": null
}
```

Status: `1` = success, other = error

## Examples

```bash
# Filter unlocked coins
sage_rpc filter_unlocked_coins '{"coin_ids": ["0xabc...", "0xdef..."]}'

# Get CAT coins for WalletConnect
sage_rpc get_asset_coins '{
  "type": "cat",
  "asset_id": "a628c1c2...",
  "limit": 20
}'

# Sign message with address
sage_rpc sign_message_by_address '{
  "message": "Login to MyDApp",
  "address": "xch1abc..."
}'

# Sign with specific pubkey
sage_rpc sign_message_with_public_key '{
  "message": "Verify ownership",
  "public_key": "0x89abcdef..."
}'

# Send transaction directly
sage_rpc send_transaction_immediately '{
  "spend_bundle": {
    "coin_spends": [...],
    "aggregated_signature": "0x..."
  }
}'
```

## WalletConnect Flow

1. dApp requests connection
2. User approves in Sage
3. dApp calls `get_asset_coins` to find spendable coins
4. dApp builds transaction
5. User signs via `sign_message_*` or transaction signing
6. dApp broadcasts or calls `send_transaction_immediately`

## Notes

- WalletConnect enables dApp ↔ wallet communication
- `lineage_proof` is required for CAT spends
- Message signing proves address ownership without spending
