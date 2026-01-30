---
name: sage-did
description: Sage DID (Decentralized Identifier) operations. List DIDs, create new DIDs, transfer ownership, update metadata, normalize.
---

# Sage DIDs

DID (Decentralized Identifier) operations.

## Endpoints

### Query DIDs

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_dids` | `{}` | List all DIDs |
| `get_minter_did_ids` | `{"offset": 0, "limit": 50}` | List minter DIDs |

### Create DID

```json
{
  "name": "My Identity",
  "fee": "100000000",
  "auto_submit": true
}
```

### Update DID

```json
{
  "did_id": "did:chia:1abc...",
  "name": "Updated Name",
  "visible": true
}
```

### Transfer DIDs

```json
{
  "did_ids": ["did:chia:1abc..."],
  "address": "xch1...",
  "fee": "100000000",
  "clawback": null,
  "auto_submit": true
}
```

### Normalize DIDs

Update DID records to latest on-chain state:

```json
{
  "did_ids": ["did:chia:1abc..."],
  "fee": "100000000",
  "auto_submit": true
}
```

## DID Record Structure

```json
{
  "did_id": "did:chia:1abc...",
  "launcher_id": "0x...",
  "name": "My Identity",
  "visible": true,
  "coin_id": "0x..."
}
```

## Examples

```bash
# List DIDs
sage_rpc get_dids '{}'

# Create DID
sage_rpc create_did '{
  "name": "Artist Profile",
  "fee": "100000000",
  "auto_submit": true
}'

# Transfer DID
sage_rpc transfer_dids '{
  "did_ids": ["did:chia:1abc..."],
  "address": "xch1newowner...",
  "fee": "100000000",
  "auto_submit": true
}'

# Update name
sage_rpc update_did '{
  "did_id": "did:chia:1abc...",
  "name": "New Profile Name",
  "visible": true
}'
```

## Use Cases

- **NFT Minting**: DIDs provide verifiable provenance for minted NFTs
- **Identity**: DIDs act as on-chain identities for profiles
- **Collections**: Link NFT collections to a minter DID
- **Authentication**: Sign messages with DID keys for verification
