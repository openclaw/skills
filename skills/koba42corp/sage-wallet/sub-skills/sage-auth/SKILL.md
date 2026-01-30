---
name: sage-auth
description: Sage wallet authentication and key management. Login/logout, generate mnemonics, import/delete keys, manage wallet identities.
---

# Sage Auth

Authentication and key management for Sage wallet.

## Endpoints

### Session Management

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `login` | `{"fingerprint": 1234567890}` | Login to wallet |
| `logout` | `{}` | End session |

### Key Management

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_keys` | `{}` | List all wallet keys |
| `get_key` | `{"fingerprint": 1234567890}` | Get specific key info |
| `get_secret_key` | `{"fingerprint": 1234567890}` | Get mnemonic (sensitive!) |
| `generate_mnemonic` | `{"use_24_words": false}` | Generate new mnemonic |
| `import_key` | See below | Import wallet from mnemonic |
| `delete_key` | `{"fingerprint": 1234567890}` | Delete wallet key |
| `rename_key` | `{"fingerprint": 1234567890, "name": "My Wallet"}` | Rename wallet |
| `set_wallet_emoji` | `{"fingerprint": 1234567890, "emoji": "🌱"}` | Set emoji |

### Import Key Payload

```json
{
  "name": "My Wallet",
  "key": "abandon abandon abandon ... about",
  "derivation_index": 0,
  "hardened": true,
  "unhardened": true,
  "save_secrets": true,
  "login": true,
  "emoji": "🌱"
}
```

### Database Management

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `resync` | `{"fingerprint": 1234567890, "delete_coins": false, ...}` | Resync wallet |
| `delete_database` | `{"fingerprint": 1234567890, "network": "mainnet"}` | Delete wallet DB |

### Themes

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_user_themes` | `{}` | List theme NFTs |
| `get_user_theme` | `{"nft_id": "nft1..."}` | Get specific theme |
| `save_user_theme` | `{"nft_id": "nft1..."}` | Save theme |
| `delete_user_theme` | `{"nft_id": "nft1..."}` | Delete theme |

## Examples

```bash
# Login
sage_rpc login '{"fingerprint": 1234567890}'

# List keys
sage_rpc get_keys '{}'

# Generate new mnemonic
sage_rpc generate_mnemonic '{"use_24_words": true}'

# Import wallet
sage_rpc import_key '{
  "name": "Trading Wallet",
  "key": "word1 word2 ... word24",
  "save_secrets": true,
  "login": true
}'
```

## Security Notes

- `get_secret_key` returns the mnemonic — handle with extreme care
- Never log or store mnemonic in plaintext
- Use `save_secrets: false` for watch-only imports
