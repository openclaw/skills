---
name: sage-offers
description: Sage offer operations for peer-to-peer trading. Create offers, view, accept, combine, import, cancel offers.
---

# Sage Offers

Peer-to-peer offer trading system.

## Endpoints

### Create Offer

```json
{
  "requested_assets": [
    {"asset_id": null, "amount": "1000000000000"}
  ],
  "offered_assets": [
    {"asset_id": "a628c1c2...", "amount": "1000"}
  ],
  "fee": "100000000",
  "receive_address": null,
  "expires_at_second": null,
  "auto_import": true
}
```

- `asset_id: null` = XCH
- Returns `{"offer": "offer1...", "offer_id": "..."}`

### Accept Offer

```json
{
  "offer": "offer1...",
  "fee": "100000000",
  "auto_submit": true
}
```

### View Offer (without accepting)

```json
{
  "offer": "offer1..."
}
```

Returns offer summary and status.

### Query Offers

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_offers` | `{}` | List all offers |
| `get_offer` | `{"offer_id": "..."}` | Get specific offer |
| `get_offers_for_asset` | `{"asset_id": "..."}` | Filter by asset |
| `import_offer` | `{"offer": "offer1..."}` | Import external offer |

### Cancel/Delete

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `delete_offer` | `{"offer_id": "..."}` | Delete local (not on-chain) |
| `cancel_offer` | `{"offer_id": "...", "fee": "...", "auto_submit": true}` | Cancel on-chain |
| `cancel_offers` | `{"offer_ids": [...], "fee": "...", "auto_submit": true}` | Bulk cancel |

### Combine Offers

Merge multiple compatible offers:

```json
{
  "offers": ["offer1...", "offer1..."]
}
```

## Offer Amount Structure

```json
{
  "asset_id": "a628c1c2...",
  "hidden_puzzle_hash": null,
  "amount": "1000"
}
```

## Offer Record Structure

```json
{
  "offer_id": "...",
  "offer": "offer1...",
  "status": "pending",
  "requested": [...],
  "offered": [...],
  "expires_at_second": null
}
```

Status values: `"pending"`, `"completed"`, `"cancelled"`, `"expired"`

## Examples

```bash
# Create offer: 1 XCH for 1000 SBX
sage_rpc make_offer '{
  "requested_assets": [{"asset_id": null, "amount": "1000000000000"}],
  "offered_assets": [{"asset_id": "a628c1c2...", "amount": "1000"}],
  "fee": "100000000",
  "auto_import": true
}'

# View offer
sage_rpc view_offer '{"offer": "offer1abc..."}'

# Accept offer
sage_rpc take_offer '{
  "offer": "offer1abc...",
  "fee": "100000000",
  "auto_submit": true
}'

# Cancel offer
sage_rpc cancel_offer '{
  "offer_id": "abc123",
  "fee": "100000000",
  "auto_submit": true
}'
```

## Notes

- Offers are bech32-encoded strings starting with `offer1`
- `delete_offer` only removes from local database
- `cancel_offer` spends offered coins on-chain to invalidate
- Combine offers for complex multi-party trades
