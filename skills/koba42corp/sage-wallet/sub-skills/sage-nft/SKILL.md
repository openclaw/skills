---
name: sage-nft
description: Sage NFT operations. List NFTs and collections, mint NFTs, transfer, add URIs, assign to DIDs, manage visibility.
---

# Sage NFTs

NFT operations for Chia NFT1 standard.

## Endpoints

### Query NFTs

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_nfts` | See below | List NFTs with filters |
| `get_nft` | `{"nft_id": "nft1..."}` | Get NFT details |
| `get_nft_icon` | `{"nft_id": "nft1..."}` | Get icon (base64) |
| `get_nft_thumbnail` | `{"nft_id": "nft1..."}` | Get thumbnail (base64) |
| `get_nft_data` | `{"nft_id": "nft1..."}` | Get raw data |

#### get_nfts Payload

```json
{
  "collection_id": null,
  "minter_did_id": null,
  "owner_did_id": null,
  "name": null,
  "offset": 0,
  "limit": 50,
  "sort_mode": "recent",
  "include_hidden": false
}
```

Sort modes: `"name"`, `"recent"`

### Collections

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_nft_collections` | `{"offset": 0, "limit": 50, "include_hidden": false}` | List collections |
| `get_nft_collection` | `{"collection_id": "col1..."}` | Get collection |
| `update_nft_collection` | `{"collection_id": "col1...", "visible": true}` | Update visibility |

### Mint NFTs

```json
{
  "mints": [
    {
      "address": null,
      "edition_number": 1,
      "edition_total": 100,
      "data_hash": "0x...",
      "data_uris": ["https://..."],
      "metadata_hash": "0x...",
      "metadata_uris": ["https://..."],
      "license_hash": null,
      "license_uris": [],
      "royalty_address": "xch1...",
      "royalty_ten_thousandths": 300
    }
  ],
  "did_id": "did:chia:...",
  "fee": "100000000",
  "auto_submit": true
}
```

Response includes `nft_ids` array.

### Transfer & Manage

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `transfer_nfts` | `{"nft_ids": [...], "address": "xch1...", "fee": "...", "auto_submit": true}` | Transfer |
| `add_nft_uri` | `{"nft_id": "...", "uri": "https://...", "kind": "data", "fee": "..."}` | Add URI |
| `assign_nfts_to_did` | `{"nft_ids": [...], "did_id": "did:chia:...", "fee": "..."}` | Assign to DID |
| `update_nft` | `{"nft_id": "...", "visible": true}` | Update visibility |
| `redownload_nft` | `{"nft_id": "..."}` | Re-fetch data |

URI kinds: `"data"`, `"metadata"`, `"license"`

## NFT Record Structure

```json
{
  "nft_id": "nft1...",
  "launcher_id": "0x...",
  "collection_id": "col1...",
  "owner_did_id": "did:chia:...",
  "minter_did_id": "did:chia:...",
  "name": "My NFT",
  "description": "...",
  "data_uris": ["https://..."],
  "metadata_uris": ["https://..."],
  "royalty_address": "xch1...",
  "royalty_ten_thousandths": 300,
  "visible": true
}
```

## Examples

```bash
# List NFTs
sage_rpc get_nfts '{"limit": 20, "sort_mode": "recent"}'

# Mint NFT
sage_rpc bulk_mint_nfts '{
  "mints": [{
    "data_uris": ["ipfs://Qm..."],
    "data_hash": "0xabc...",
    "metadata_uris": ["ipfs://Qm..."],
    "metadata_hash": "0xdef...",
    "royalty_ten_thousandths": 500
  }],
  "did_id": "did:chia:1abc...",
  "fee": "100000000",
  "auto_submit": true
}'

# Transfer NFT
sage_rpc transfer_nfts '{
  "nft_ids": ["nft1abc..."],
  "address": "xch1recipient...",
  "fee": "100000000",
  "auto_submit": true
}'
```

## Notes

- Royalty is in ten-thousandths: 300 = 3%, 500 = 5%
- `did_id: null` in `assign_nfts_to_did` unassigns from DID
- Minting requires a DID for provenance
