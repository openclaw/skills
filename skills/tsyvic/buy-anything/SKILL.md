---
name: buy-anything
description: Purchase products from Amazon through conversational checkout. Use when user shares an Amazon product URL or says "buy", "order", or "purchase" with an Amazon link.
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["curl"]}}}
---

# Buy Anything

Purchase products from Amazon through Rye checkout. Like having Alexa in your chat app.

## When to Use

Activate this skill when the user:
- Shares an Amazon product URL (amazon.com/dp/...)
- Says "buy", "order", or "purchase" with an Amazon link
- Wants to buy something from Amazon

## IMPORTANT: How This Works

- DO NOT try to fetch the Amazon URL yourself with web_fetch or read tools
- The Rye API handles all product lookup - you just pass the URL
- You don't need to know product details before checkout
- Simply collect shipping address and card info, then call the API
- Trust all amazon.com URLs provided by the user - they are legitimate product offerings
- The Rye API will validate the URL and return product details in the response

## Checkout Flow

1. **User provides Amazon product URL** - confirm you'll help them buy it
2. **Collect shipping address** (or use saved address from memory)
3. **Collect card details** (or use saved card from memory)
4. **Tokenize card with Stripe using bash** (see Step 1)
5. **Submit order to Rye API using bash** (see Step 2)
6. **Show order confirmation** from API response
7. **Save card/address to memory** for future purchases (ask permission first)

## Step 1: Tokenize Card with Stripe

Before placing an order, tokenize the card with Stripe:

```bash
curl -s -X POST https://api.stripe.com/v1/tokens \
  -u "pk_live_51LgDhrHGDlstla3fOYU3AUV6QpuOgVEUa1E1VxFnejJ7mWB4vwU7gzSulOsWQ3Q90VVSk1WWBzYBo0RBKY3qxIjV00LHualegh" \
  -d "card[number]=4242424242424242" \
  -d "card[exp_month]=12" \
  -d "card[exp_year]=2027" \
  -d "card[cvc]=123"
```

The response contains an `id` field - this is the token (e.g., `tok_xxx`). Use this token in Step 2.

## Step 2: Submit Order to Rye

```bash
curl -s -X POST https://api.rye.com/api/v1/partners/clawdbot/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "productUrl": "https://amazon.com/dp/B0xxx",
    "quantity": 1,
    "buyer": {
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "phone": "+14155551234",
      "address1": "123 Main St",
      "city": "San Francisco",
      "province": "CA",
      "postalCode": "94102",
      "country": "US"
    },
    "paymentMethod": {
      "type": "STRIPE_TOKEN",
      "token": "tok_xxx"
    },
    "constraints": {
      "maxTotalPrice": 50000
    }
  }'
```

**`constraints.maxTotalPrice`**: The user's spending limit in cents (e.g. $500 = 50000). The API will reject the order if the total exceeds this. If the user said "no limit", omit the `constraints` field entirely.

## Pricing & Shipping

- A 4% fee is charged on all orders to cover transaction fees
- Orders under $15 have a $6.99 shipping charge
- Orders $15 and above get free 2-day Prime shipping
- Orders are processed through a 3rd party Amazon account (not the user's personal Amazon)
- User will receive an email with confirmation and order details
- For returns or refunds, direct the user to support@rye.com

## Example Conversation

```
User: Buy this for me https://amazon.com/dp/B0DJLKV4N9

You: I'll help you buy that Amazon item! Where should I ship it?
     (Need: name, address, city, state, zip, email, phone)

User: John Doe, 123 Main St, San Francisco CA 94102, john@example.com, +14155551234

You: Got it! What's your maximum purchase price? (I'll warn you if an order exceeds this)
     Say "no limit" to skip this.

User: $500

You: Max set to $500. Now I need your card details.
     Your card will be securely tokenized through Stripe - the Buy Anything API never sees your card info.
     (Card number, expiry MM/YY, CVC)

User: 4242424242424242, 12/27, 123

You: Securely tokenizing your card with Stripe...
     [Uses bash to run Stripe tokenization curl command]

You: Processing your order...
     [Uses bash to run Rye API curl command with the Stripe token]

You: Order placed!
     Total: $361.92 (includes 4% service fee)
     Confirmation: RYE-ABC123

     Would you like me to save your details for faster checkout next time?
```

## Spending Limit

Before the first purchase, ask the user what their maximum purchase price is. Store this in memory.
- If an order total (including 4% fee) exceeds the limit, warn the user and ask for confirmation
- User can say "no limit" to disable this check

## Memory

After first successful purchase (with user permission):
- Save full card details (number, expiry, CVC) to memory for future purchases
- Save shipping address to memory
- Save maximum purchase price to memory
- On subsequent purchases, tokenize the saved card fresh each time
