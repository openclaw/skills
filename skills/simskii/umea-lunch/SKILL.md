---
name: umea-lunch
description: Get today's lunch menus from restaurants in Umeå. Use when asking about lunch, restaurants, or food in Umeå. Fetches live data from umealunchguide.se.
---

# Umeå Lunch Guide

Fetch and display lunch menus from Umeå restaurants via umealunchguide.se.

## Quick Start

Run the script to get today's menus:

```bash
python3 /root/clawd/skills/umea-lunch/scripts/fetch_lunch.py
```

### Options

```bash
# Get menus for a specific date (YYYY-MM-DD)
python3 /root/clawd/skills/umea-lunch/scripts/fetch_lunch.py --date 2026-01-29

# Filter by restaurant name (case-insensitive partial match)
python3 /root/clawd/skills/umea-lunch/scripts/fetch_lunch.py --restaurant tonka

# List all available restaurants
python3 /root/clawd/skills/umea-lunch/scripts/fetch_lunch.py --list

# Combine filters
python3 /root/clawd/skills/umea-lunch/scripts/fetch_lunch.py --date 2026-01-29 --restaurant "o'learys"
```

## Output Format

The script outputs JSON with restaurant info and lunch courses:

```json
{
  "date": "2026-01-28",
  "restaurants": [
    {
      "name": "Restaurant Name",
      "address": "Street 123",
      "phone": "090-123456",
      "website": "https://...",
      "courses": [
        {
          "title": "Dish Name",
          "description": "Description of the dish",
          "price": "149",
          "tags": ["Vegetarisk", "Glutenfri"]
        }
      ]
    }
  ]
}
```

## Response Guidelines

When presenting lunch options:
- Group by restaurant
- Show dish name, description, and price
- Mention dietary tags (🥗 vegetarisk, 🌱 vegansk, 🌾 glutenfri, 🥛 laktosfri)
- Include address if user needs directions
