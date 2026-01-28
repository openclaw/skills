# Willhaben Bot Setup

On first use, check if `config/user-preferences.json` exists. If not, run this setup.

## Setup Questions

Ask these one by one, conversationally. Don't dump all at once.

### 1. Location
"Wo bist du? (Bezirk/Stadt für Abholung)"
- Store: `location.bezirk`, `location.city`, `location.display`

### 2. Shipping
"Wie willst du normalerweise übergeben?"
- Nur Selbstabholung
- Versand möglich (privat)
- PayLivery (Käuferschutz)
- Alles offen lassen
- Store: `shipping.*`

### 3. Description Style  
"Beschreibungen: kurz & casual oder ausführlich?"
- Kurz (empfohlen) - 2-3 Sätze
- Ausführlich - alle Details
- Store: `description_style.length`

### 4. Pricing Strategy
"Preisstrategie?"
- Schnell verkaufen (unter Marktpreis)
- Ausgewogen (Marktpreis)
- Geduldig (über Marktpreis, VB)
- Store: `pricing.strategy`

### 5. Privatverkauf Disclaimer
"Standard 'Privatverkauf, keine Garantie' anhängen?"
- Ja (empfohlen)
- Nein
- Store: `description_style.include_privatverkauf_disclaimer`

## After Setup

1. Write answers to `config/user-preferences.json`
2. Set `setup_complete: true`
3. Confirm: "Setup fertig! Deine Einstellungen sind gespeichert. Schick mir ein Foto wenn du was verkaufen willst."

## Using Preferences

When creating listings, read `config/user-preferences.json` and apply:
- Auto-fill location
- Add shipping info based on preferences
- Use description style
- Apply pricing strategy to recommendations
- Add disclaimer if enabled
