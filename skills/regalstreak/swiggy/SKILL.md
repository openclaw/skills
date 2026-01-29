---
name: swiggy
description: "Order food, groceries, and book restaurants in India via Swiggy's MCP servers. Food delivery, Instamart groceries, and Dineout restaurant bookings with safety-first confirmation workflow."
---

# Swiggy Skill

Order food, groceries, and book restaurants in India via Swiggy's MCP servers.

## Installation

The skill includes a `swiggy` CLI binary. After installing the skill:
```bash
cd skills/swiggy
npm link
```

This creates a global `swiggy` command. Verify with: `which swiggy`

## When to Use

- Food delivery: "Order biryani", "What's open late?", "Team lunch for 8"
- Groceries (Instamart): "Get eggs and milk", "Weekly groceries", "Recipe ingredients"
- Restaurant bookings (Dineout): "Book dinner Saturday 8pm", "Italian in Koramangala"

## Available Commands

### Food Delivery

```bash
# Search restaurants
swiggy food search "biryani" --location "Koramangala, Bengaluru"

# Get menu
swiggy food menu <restaurant-id>

# Cart management
swiggy food cart add <item-id> --quantity 2
swiggy food cart show
swiggy food cart clear

# Order (requires confirmation)
swiggy food order --address "home" --confirm
```

### Instamart (Groceries)

```bash
# Search products
swiggy im search "eggs" --location "HSR Layout, Bengaluru"

# Cart operations
swiggy im cart add <item-id> --quantity 3
swiggy im cart show
swiggy im cart clear

# Checkout (requires confirmation)
swiggy im order --address "home" --confirm
```

### Dineout (Restaurant Bookings)

```bash
# Search restaurants
swiggy dineout search "Italian Indiranagar"

# Get details
swiggy dineout details <restaurant-id>

# Check availability
swiggy dineout slots <restaurant-id> --date 2026-01-30

# Book table (free bookings only, requires confirmation)
swiggy dineout book <restaurant-id> --date 2026-01-30 --time 20:00 --guests 2 --confirm
```

## CRITICAL: Safety Rules

### ⚠️ NEVER Auto-Order
**ALWAYS get explicit confirmation before placing orders.**

1. **Show cart preview first:**
   - All items with quantities and prices
   - Total amount
   - Delivery address
   - Estimated delivery time (food/groceries)

2. **Ask for confirmation:**
   ```
   Ready to order:
   - 2x Chicken Biryani (₹500)
   - 1x Raita (₹60)
   Total: ₹560 + delivery
   Deliver to: Home (HSR Layout)
   ETA: 30-40 mins
   
   Confirm order? (yes/no)
   ```

3. **Only after user says YES:**
   - Run the order command with `--confirm` flag
   - Log to `memory/swiggy-orders.json`

### COD Warning
Swiggy MCP currently supports **Cash on Delivery only**. Orders **cannot be cancelled** once placed. Always double-check before confirming.

### Address Handling
- User may say "home", "office", etc. - map to actual addresses from USER.md or ask
- Always confirm delivery location in preview
- For Dineout, location is used for search only (not delivery)

## Workflow Examples

### Food Order Flow
```bash
# 1. Search
swiggy food search "biryani near Koramangala"

# 2. Browse menu (use restaurant ID from search)
swiggy food menu rest_12345

# 3. Add to cart
swiggy food cart add item_67890 --quantity 1

# 4. Preview cart
swiggy food cart show

# 5. Show preview to user, ask confirmation

# 6. If confirmed, order
swiggy food order --address "HSR Layout, Sector 2, Bengaluru" --confirm
```

### Grocery Shopping Flow
```bash
# 1. Search items
swiggy im search "eggs" --location "Koramangala"
swiggy im search "milk" --location "Koramangala"

# 2. Add to cart
swiggy im cart add item_11111 --quantity 2
swiggy im cart add item_22222 --quantity 1

# 3. Preview
swiggy im cart show

# 4. Confirm with user

# 5. Checkout
swiggy im order --address "Koramangala, Bengaluru" --confirm
```

### Restaurant Booking Flow
```bash
# 1. Search
swiggy dineout search "Italian Indiranagar"

# 2. Check details
swiggy dineout details rest_99999

# 3. Check slots
swiggy dineout slots rest_99999 --date 2026-01-30

# 4. Show options to user, confirm choice

# 5. Book
swiggy dineout book rest_99999 --date 2026-01-30 --time 20:00 --guests 2 --confirm
```

## Error Handling

- **No results:** Suggest broader search or different location
- **Out of stock:** Show alternatives
- **No slots available:** Suggest different times/dates
- **Authentication required:** User needs to authenticate via OAuth (handled by MCP)

## Tips

- For team orders: build cart iteratively, ask for preferences
- For budget shopping: filter results by price, show running total
- For recipe-to-cart: search each ingredient, add progressively
- For late night: mention delivery time in search criteria

## Order Logging

After successful order, append to `memory/swiggy-orders.json`:
```json
{
  "timestamp": "2026-01-28T21:16:00+05:30",
  "type": "food",
  "items": [...],
  "total": "₹560",
  "address": "HSR Layout",
  "orderId": "..."
}
```

## Authentication

Swiggy MCP uses OAuth. First use will trigger auth flow. The `swiggy` CLI handles this via mcporter.

## Dependencies

- Requires `mcporter` skill (uses it under the hood)
- Node.js runtime for the CLI wrapper

## Known Limitations

- COD only (no online payment yet)
- Orders cannot be cancelled
- Dineout: free bookings only
- Don't open Swiggy app while using MCP (session conflicts)

---

**Remember: Confirmation BEFORE ordering. Every. Single. Time.** 🐾
