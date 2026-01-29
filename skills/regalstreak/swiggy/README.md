# Swiggy Skill for Clawdbot

Order food, groceries, and book restaurant tables in India through your AI agent.

## What It Does

This skill integrates Swiggy's MCP servers into Clawdbot:

- **Food Delivery** - Search restaurants, browse menus, order food
- **Instamart** - Grocery shopping and delivery
- **Dineout** - Restaurant discovery and table bookings

## Installation

**Via ClawdHub:**
```bash
clawdhub install swiggy
cd skills/swiggy
npm link
```

**Manual:**
```bash
cd ~/clawd/skills/swiggy
npm link
```

This makes the `swiggy` command available globally.

**Verify installation:**
```bash
which swiggy
swiggy  # Should show usage help
```

## Quick Start

### Food Delivery

```bash
# Search for restaurants
swiggy food search "biryani" --location "Koramangala, Bengaluru"

# Browse menu
swiggy food menu rest_12345

# Add to cart
swiggy food cart add item_67890 --quantity 2

# View cart
swiggy food cart show

# Place order (requires --confirm flag)
swiggy food order --address "HSR Layout, Bengaluru" --confirm
```

### Groceries (Instamart)

```bash
# Search products
swiggy im search "eggs" --location "HSR Layout"

# Add to cart
swiggy im cart add prod_11111 --quantity 2

# Checkout
swiggy im order --address "HSR Layout, Bengaluru" --confirm
```

### Restaurant Bookings (Dineout)

```bash
# Search restaurants
swiggy dineout search "Italian Indiranagar"

# Check availability
swiggy dineout slots rest_99999 --date 2026-01-30

# Book table
swiggy dineout book rest_99999 --date 2026-01-30 --time 20:00 --guests 2 --confirm
```

## Safety Features

### Confirmation Required

The `--confirm` flag is **mandatory** for all orders and bookings. This prevents accidental purchases.

Without `--confirm`:
```bash
swiggy food order --address "home"
# ❌ Error: --confirm flag required
```

With `--confirm`:
```bash
swiggy food order --address "home" --confirm
# ✅ Order placed
```

### Always Preview First

**Workflow:**
1. Build cart (`cart add`)
2. Preview (`cart show`)
3. Confirm with user
4. Order (`order --confirm`)

### COD Only

⚠️ Currently supports **Cash on Delivery only**. Orders **cannot be cancelled** after placement.

## How It Works

The skill uses `mcporter` to connect to Swiggy's HTTP MCP servers:

- Food: `https://mcp.swiggy.com/food`
- Instamart: `https://mcp.swiggy.com/im`
- Dineout: `https://mcp.swiggy.com/dineout`

## Authentication

First use will trigger OAuth flow. Follow the prompts to authenticate with your Swiggy account.

## Use Cases

### "Order me lunch"
```
User: Order biryani for lunch
Agent: 
  1. searches "biryani near <location>"
  2. shows top results
  3. user picks restaurant
  4. browses menu
  5. adds to cart
  6. shows preview with total
  7. asks for confirmation
  8. places order with --confirm
```

### "Weekly groceries"
```
User: Get eggs, milk, bread
Agent:
  1. searches each item
  2. adds to cart
  3. shows cart total
  4. confirms address
  5. places order
```

### "Book dinner"
```
User: Italian dinner Saturday 8pm for 2 in Koramangala
Agent:
  1. searches restaurants
  2. checks slots
  3. shows options
  4. books with --confirm
```

## Limitations

- COD only (no online payment yet)
- Orders cannot be cancelled
- Dineout: free bookings only
- Don't use Swiggy app simultaneously (session conflicts)

## Dependencies

- Node.js ≥ 18
- `mcporter` skill (must be installed)
- Active internet connection
- Swiggy account (for OAuth)

## Troubleshooting

**"mcporter not found"**
→ Install the mcporter skill first

**"Authentication failed"**
→ Run `mcporter auth --server https://mcp.swiggy.com/food` manually

**"No results found"**
→ Try broader search terms or different location

**"Session conflict"**
→ Close Swiggy app before using MCP

## Credits

Built for Clawdbot by Neil Agarwal.

MCP servers provided by Swiggy (https://github.com/Swiggy/swiggy-mcp-server-manifest).

## License

MIT
