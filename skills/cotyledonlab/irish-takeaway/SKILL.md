---
name: irish-takeaway
description: Find nearby takeaways in Ireland and browse menus via Deliveroo/Just Eat. Uses Google Places API for discovery and browser automation for menu scraping.
metadata: {"clawdbot":{"emoji":"🍕","requires":{"bins":["goplaces"],"env":["GOOGLE_PLACES_API_KEY"]}}}
---

# Irish Takeaway Finder 🍕🇮🇪

Find nearby takeaways and get their menus from Deliveroo or Just Eat.

## Prerequisites

- `goplaces` CLI installed (`brew install steipete/tap/goplaces`)
- `GOOGLE_PLACES_API_KEY` environment variable set
- Browser tool available

## Workflow

### Step 1: Find Nearby Takeaways

Use goplaces to search for restaurants near a location:

```bash
# Search by coordinates (negative longitude needs = syntax)
goplaces search "takeaway" --lat=53.7179 --lng=-6.3561 --radius-m=3000 --limit=10

# Search by cuisine
goplaces search "chinese takeaway" --lat=53.7179 --lng=-6.3561 --radius-m=2000

# Filter by rating
goplaces search "pizza" --lat=53.7179 --lng=-6.3561 --min-rating=4 --open-now
```

Common location coordinates for Ireland:
- **Drogheda**: 53.7179, -6.3561
- **Dublin City**: 53.3498, -6.2603
- **Cork**: 51.8985, -8.4756
- **Galway**: 53.2707, -9.0568

### Step 2: Get Deliveroo Menu (Browser Automation)

1. Start browser and navigate to Deliveroo:
```
browser action=start target=host
browser action=navigate targetUrl="https://deliveroo.ie/" target=host
```

2. Accept cookies if prompted (look for "Accept all" button)

3. Enter location in address search box:
```
browser action=act request={"kind": "type", "ref": "<textbox-ref>", "text": "Drogheda, Co. Louth"}
```

4. Select location from autocomplete dropdown

5. Find and click on restaurant from list

6. Take snapshot to extract menu items - look for:
   - Category headings (h2)
   - Item buttons with name, description, price
   - Allergen info in item descriptions

### Step 3: Parse Menu Data

Menu items typically appear as buttons with structure:
- **Name**: In paragraph element
- **Description**: In text content
- **Price**: Usually "€X.XX" format
- **Allergens**: Listed after description (Gluten, Milk, etc.)

### Example Conversation Flow

User: "What takeaways are near me in Drogheda?"
→ Run goplaces search, present top 5-10 results with ratings

User: "Show me the menu for Mizzoni's"
→ Browser to Deliveroo → search → click restaurant → snapshot → parse menu

User: "What pizzas do they have?"
→ Filter menu items by category, present pizza options with prices

### Just Eat Alternative

If restaurant not on Deliveroo, try Just Eat:
```
browser action=navigate targetUrl="https://www.just-eat.ie/" target=host
```

Similar flow: enter postcode/address → browse restaurants → click for menu

### Tips

- Always dismiss cookie banners first
- Wait for autocomplete suggestions before clicking
- Some restaurants have "Limited order tracking" - still works for menu viewing
- Prices include allergen info in descriptions
- Use snapshot with compact=true for cleaner output

### Menu Categories to Look For

- Meal Deals & Special Offers
- Pizzas (by size: Small/Medium/Large/XL/Wagon Wheel)
- Starters
- Pasta
- Burgers
- Sides
- Desserts
- Drinks

## Future Enhancements

- [ ] Twilio voice integration for phone ordering
- [ ] Price comparison across platforms
- [ ] Favorite restaurants memory
- [ ] Order history tracking
