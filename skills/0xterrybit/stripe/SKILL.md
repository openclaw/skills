---
name: stripe
description: Stripe payment platform integration. Manage payments, subscriptions, invoices, and customers via Stripe API.
metadata: {"clawdbot":{"emoji":"💵","always":true,"requires":{"bins":["curl","jq"]},"primaryEnv":"STRIPE_API_KEY"}}
---

# Stripe 💵

Stripe payment platform integration.

## Setup

```bash
export STRIPE_API_KEY="sk_live_..."
```

## Features

- Create payment intents
- Manage subscriptions
- Send invoices
- Customer management
- Refund processing
- Webhook handling

## Usage Examples

```
"Create a $50 payment link"
"List recent Stripe payments"
"Refund payment pi_xxx"
"Show subscription for customer@email.com"
```

## API Reference

```bash
# List recent charges
curl -s https://api.stripe.com/v1/charges?limit=10 \
  -u "$STRIPE_API_KEY:"
```
