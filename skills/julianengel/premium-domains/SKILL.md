---
name: premium-domains
description: Search for premium domains for sale across Afternic, Sedo, Atom, Dynadot, Namecheap, NameSilo, and Unstoppable Domains.
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["curl"]}}}
---

# Premium Domain Search

Find domains for sale across major marketplaces. Free API, just curl.

## Usage

```bash
curl -s "https://api.domaindetails.com/api/marketplace/search?domain=example.com" | jq
```

## Marketplaces Checked

- **Afternic** — GoDaddy's premium marketplace
- **Sedo** — Global domain trading platform
- **Atom** — Premium domain marketplace
- **Dynadot** — Auctions & buy-now listings
- **Namecheap** — Integrated registrar marketplace
- **NameSilo** — Budget-friendly marketplace
- **Unstoppable Domains** — Web3 domains

## Response Fields

- `found` — whether any listings exist
- `marketplaces.<name>.listing.price` — price in cents or dollars
- `marketplaces.<name>.listing.currency` — USD, EUR, etc.
- `marketplaces.<name>.listing.url` — direct link to listing
- `marketplaces.<name>.listing.listingType` — buy_now, auction, make_offer

## Rate Limits

- 100 requests/minute (no auth needed)
