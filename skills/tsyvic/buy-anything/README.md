# buy-anything

A Clawdbot skill for purchasing products from Amazon. Like having Alexa in your chat app.

## Installation

### Via ClawdHub (recommended)

```bash
# If you have clawdhub installed
clawdhub install buy-anything

# Or use npx
npx clawdhub install buy-anything
```

Don't have clawdhub? Install it:
```bash
npm install -g clawdhub
```

### Manual

Copy this folder to your Clawdbot skills directory:

```bash
# Global installation
cp -r . ~/.clawdbot/skills/buy-anything

# Or workspace installation
cp -r . ./skills/buy-anything
```

## Usage

Just ask Clawdbot to buy something from Amazon:

```
You: Buy this for me https://amazon.com/dp/B0DJLKV4N9

Clawdbot: I'll help you buy that! Where should I ship it?

You: John Doe, 123 Main St, San Francisco CA 94102, john@example.com, +14155551234

Clawdbot: Got it! What's your max purchase price? (I'll warn you before exceeding it)

You: $500

Clawdbot: Now I need your card details.
          Your card will be securely tokenized through Stripe.

You: 4242424242424242, 12/27, 123

Clawdbot: Order placed!
          Total: $361.92 (includes 4% fee)
          Confirmation: RYE-ABC123

          Want me to save your details for next time?
```

After saving, future purchases are one message:

```
You: Buy this https://amazon.com/dp/B0CXXX

Clawdbot: Order placed! Total: $29.99 + $1.20 fee = $31.19
```

## How Payments Work

### The short version

Your card number goes directly to Stripe (the same payment processor used by Amazon, Shopify, and most of the internet). Stripe turns it into a one-time token. That token — not your card number — is what gets sent to place the order. The Buy Anything skill and the Rye API never see your raw card details.

### Under the hood

```
You type card info
        │
        ▼
┌──────────────┐
│   Stripe     │ ← Card goes here (PCI-certified processor)
│   Tokenize   │
└──────┬───────┘
       │ tok_xxx (one-time token)
       ▼
┌──────────────┐
│   Rye API    │ ← Only sees the token, never your card
│   Purchase   │
└──────┬───────┘
       │
       ▼
  Order placed on Amazon
```

1. **You provide your card** — number, expiry, CVC
2. **Stripe tokenizes it** — your card details are sent directly to Stripe's PCI-compliant API via HTTPS. Stripe returns a one-time token (e.g. `tok_abc123`)
3. **Token is used to pay** — the Rye API receives only the token to place the Amazon order. Your raw card number never touches Rye's servers
4. **Stripe handles the charge** — Stripe processes the payment using the token, just like any online checkout

This is the same tokenization flow used by every major e-commerce site. Your card number is never stored or transmitted outside of Stripe.

### Saved cards

When you save your card for future purchases, your details are stored **locally in Clawdbot's memory on your device**. They never leave your machine. Each time you make a purchase, Clawdbot re-tokenizes the saved card with Stripe to get a fresh one-time token.

## Guardrails

### Spending limit

On your first purchase, Clawdbot will ask you to set a maximum purchase price. If any order (including the 4% fee) would exceed your limit, Clawdbot will warn you and ask for confirmation before proceeding. You can say "no limit" to skip this.

You can update your limit at any time by telling Clawdbot:

```
You: Set my max purchase to $200
You: Remove my spending limit
```

### Order confirmations

Every order sends an email confirmation to the address you provide, so you always have a receipt and tracking info.

## Pricing & Shipping

- A 4% fee is charged on all orders to cover transaction fees
- Orders under $15 have a $6.99 shipping charge
- Orders $15 and above get free 2-day Prime shipping

## Good to Know

- Orders are processed through a third-party Amazon account — you can't connect orders to your personal Amazon account at this time
- You'll receive an email with order confirmation and details after each purchase
- For returns or refunds, contact support@rye.com

## Legal

By using this skill, you agree to Rye's [Terms of Service](https://rye.com/terms-of-service) and [Privacy Policy](https://rye.com/privacy-policy).

## Support

- Issues: https://github.com/rye-com/clawdbot-buy-anything/issues
- Rye API docs: https://docs.rye.com
