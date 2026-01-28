---
name: willhaben
description: Create and manage listings on Willhaben.at (Austrian marketplace). Use when the user wants to sell something, create a listing, or mentions Willhaben. Handles photo uploads, generates titles/descriptions/prices, and posts via browser automation.
---

# Willhaben Listing Creator

Create listings on Willhaben.at via browser automation.

## First-Time Setup

Check if `config/user-preferences.json` exists in the skill folder.
- If missing → run setup flow (see `references/SETUP.md`)
- If exists → read preferences and apply to all listings

User preferences include: location, shipping, description style, pricing strategy, disclaimers.

## Workflow

### 1. Receive Item Details
- User sends photos (via WhatsApp/chat)
- Optional: user provides details (condition, category, price range)

### 2. Market Research
Before suggesting a price, search Willhaben for similar/identical items:
- Search willhaben.at for the item
- Note price range of comparable listings
- Check sold prices if available
- Report findings to user:
  - **Neupreis** (new price)
  - **Marktpreis** (what similar items are listed for)
  - **Empfohlener Preis** (recommended selling price)

### 3. Generate Listing
- Analyze photos to understand the item
- Generate:
  - **Title**: Concise, searchable (German)
  - **Description**: SHORT and casual - real people don't write essays. 2-3 sentences max. Mention key facts only.
  - **Price**: Based on market research, suggest realistic price
  - **Package size**: Estimate weight category for shipping (3kg / 10kg / 31.5kg)
- Ask user:
  - Location (Bezirk) - if not in preferences
  - Any damage/issues to mention
  - If they want a more detailed description (default: no)
- Present draft for confirmation **including package size estimate**

### Listing Summary Template
Show the user something like:
```
📝 Listing Draft

Title: [title]
Description: [description]
Price: €XX VB
Location: [location]
Pickup: ✅ / Shipping: ✅

📦 Package: ~Xkg (selecting [size] package)
   → If wrong, let me know!

Photos: X attached

Ready to post?
```

If package weight is unclear (e.g., unusual item), **ask the user** rather than guessing wrong.

### 4. Post to Willhaben
See detailed browser automation steps below.

## Description Style

**Default: Casual & short**
```
Blue Yeti USB Mikrofon, schwarz. Funktioniert einwandfrei, inkl. Kabel und Standfuß. Privatverkauf, keine Garantie/Rücknahme.
```

**NOT like this (too AI/formal):**
```
Zum Verkauf steht ein hochwertiges Blue Yeti USB Kondensatormikrofon in der eleganten Blackout Edition. Dieses professionelle Mikrofon eignet sich perfekt für Podcasting, Streaming, Gaming oder Home-Office...
```

Only add detail if user explicitly asks for it.

## Language

All listings in **German** (Austrian market). Keep it natural, like a real person wrote it.

---

# Browser Automation Guide

Use `clawd` browser profile with saved Willhaben login.

## Step 1: Start Listing

1. Navigate to: `https://www.willhaben.at/iad/anzeigenaufgabe`
2. Click **"Kostenlose Anzeige aufgeben"** (link to Marktplatz free listing)

## Step 2: Fill Details Page

The form has these fields:

### Images
- **Upload method**: Use browser `upload` action with `inputRef` pointing to the "Bild auswählen" button
- Example: `browser upload inputRef=e12 paths=[...]` where e12 is the button ref
- Can upload multiple images at once via paths array
- After upload, verify images appear as thumbnails before proceeding

### Price (Verkaufspreis)
- Textbox, just enter the number (no € symbol needed)

### Title (Titel)
- Textbox with placeholder "z.B. Levi's 501 Jeans, schwarz, Größe 32"
- Keep concise and searchable

### Category (Kategorie)
- **Auto-suggests based on title** - a radio option appears
- **IMPORTANT**: Must click the category option to select it (even if it looks selected)
- If wrong category suggested, click "Andere Kategorie wählen"

### Condition (Zustand)
- Appears AFTER category is selected
- Options: Neu / Neuwertig / Gebraucht / Defekt
- Usually select "Gebraucht" for used items

### Description (Beschreibung)
- Rich text editor (contenteditable paragraph)
- Click on the paragraph area first, then type
- Keep it short!

### Contact & Location
- Pre-filled from account settings
- Shows name, email, address

## Step 3: Click "Weiter"

Proceeds to shipping options.

## Step 4: Shipping Page (Übergabe & Versand)

### Delivery Options
- **Selbstabholung**: Pickup (usually keep checked)
- **Versand**: Shipping (check if offering shipping)

### PayLivery (willhaben's shipping service)
If Versand is checked:

**Package Size (Versandgröße)** - Choose based on actual item weight!
- **Paket bis 3 kg** - Small items
- **Paket bis 10 kg** - Medium items (electronics, small appliances)
- **Paket bis 31,5 kg** - Heavy items (appliances with compressors, etc.)

Example weights:
- Ice cream maker with compressor: ~9kg → select 10kg
- Keyboard/mouse: ~1kg → select 3kg
- Monitor: ~5kg → select 10kg
- Books/games: ~0.5kg → select 3kg
- Laptop: ~2-3kg → select 3kg
- Kitchen appliance (mixer, blender): ~3-5kg → select 10kg

**⚠️ If weight is unclear**: This should have been confirmed with user in the listing summary step. If you reach this point unsure, go back and ask!

**Carrier**: Post or DPD (Post is default, fine for most)

**Sperrgut**: Check if item is oversized (>100×60×60cm) or non-rectangular

Buyer pays shipping (shown at bottom).

## Step 5: Click "Weiter"

Proceeds to upsells page.

## Step 6: Upsells Page (Zusatzprodukte)

Shows paid promotion options:
- Anzeige vorreihen (€14.99)
- Farblich hervorheben (€7.99)
- TOP Anzeige options (€21.99 - €89.99)

**Skip all** - just click **"Veröffentlichen"** to publish for free.

Shows "Gewählt: € 0" at bottom confirming no paid options.

## Step 7: Success!

Confirmation page shows:
- ✅ "Anzeige erfolgreich aufgegeben"
- Listing preview with image
- **willhaben-Code**: The listing ID (e.g., 1832624977)
- Note: "Die Veröffentlichung kann bis zu 24h dauern" (review period)

**Listing URL**: `https://www.willhaben.at/iad/object?adId={willhaben-code}`

---

# Troubleshooting

### Category not selecting
Even if the category appears, you must click on the radio/option area to actually select it. The validation error "Kategorie muss gewählt werden" means it wasn't clicked.

### Images not uploading
Use `inputRef` with the "Bild auswählen" button reference (e.g., `inputRef=e12`). Do NOT use `selector: input[type="file"]` - it doesn't work reliably on this site.

### Element refs going stale
Always take a fresh snapshot before interacting. Refs change after page updates.

### Login required
If not logged in, the profile should have saved credentials. If needed, navigate to login page or ask user to log in manually in the browser.

---

# Quick Reference

| Step | URL/Action |
|------|------------|
| Start | `https://www.willhaben.at/iad/anzeigenaufgabe` |
| Free listing | Click "Kostenlose Anzeige aufgeben" |
| Upload images | `upload` with `inputRef` pointing to "Bild auswählen" button |
| Next | "Weiter" button |
| Publish | "Veröffentlichen" button |
| View listing | `https://www.willhaben.at/iad/object?adId={ID}` |
