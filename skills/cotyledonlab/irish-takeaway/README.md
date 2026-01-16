# 🍕 Irish Takeaway Finder

A Clawdbot skill for finding nearby takeaways in Ireland and browsing their menus.

## Features

- 🔍 **Find nearby takeaways** using Google Places API
- 📋 **Browse menus** via Deliveroo/Just Eat browser automation
- 🇮🇪 **Irish-focused** with pre-configured town coordinates
- ⭐ **Filter by rating**, cuisine type, and open status

## Setup

1. Install goplaces: `brew install steipete/tap/goplaces`
2. Set API key: `export GOOGLE_PLACES_API_KEY="your-key"`

## Quick Search

```bash
# Find takeaways in Drogheda
./search-takeaways.sh drogheda

# Find pizza places in Dublin
./search-takeaways.sh dublin pizza

# Find Chinese food in Cork within 2km
./search-takeaways.sh cork chinese 2000
```

## Supported Locations

- Drogheda, Dublin, Cork, Galway, Limerick
- Waterford, Dundalk, Swords, Navan, Bray

## Menu Browsing

The skill uses browser automation to:
1. Navigate to Deliveroo.ie or Just-Eat.ie
2. Enter your location
3. Find and select the restaurant
4. Extract the full menu with prices

See SKILL.md for detailed browser automation workflow.

## Roadmap

- [ ] Twilio voice ordering integration
- [ ] Price comparison across platforms
- [ ] Order favorites/history
- [ ] Direct ordering support

---

Made with 👻 by OhMyClawd
