---
name: bring-shopping
description: Manage Bring! shopping lists via the unofficial bring-shopping Node.js library using email/password login. Use for listing lists, reading items, adding/removing items, and checking/unchecking items when API-style access is acceptable.
---

# Bring Shopping

## Overview

Use the `bring-shopping` npm package to access Bring! lists with email/password credentials. Default list is "Willig" unless the user specifies otherwise.

## Quick Start

1. Install dependency in the skill folder:
   - `npm install bring-shopping`
2. Set environment variables in the Clawdbot config (preferred) or shell:
   - `BRING_EMAIL` and `BRING_PASSWORD`
3. Run the CLI script:
   - `node scripts/bring_cli.mjs items --list "Willig"`

## Tasks

### Show lists

- `node scripts/bring_cli.mjs lists`

### Show items

- `node scripts/bring_cli.mjs items --list "Willig"`

### Add items

- `node scripts/bring_cli.mjs add --item "Milch" --spec "2L" --list "Willig"`

### Remove items

- `node scripts/bring_cli.mjs remove --item "Milch" --list "Willig"`

### Check items

- `node scripts/bring_cli.mjs check --item "Milch" --list "Willig"`

### Uncheck items

- `node scripts/bring_cli.mjs uncheck --item "Milch" --spec "2L" --list "Willig"`

## Notes

- Store credentials in Clawdbot config env so they are not bundled with the skill.
- If the list name is ambiguous, run `lists` and ask which list to use.
- If an item is already checked, `uncheck` re-adds it to the purchase list.
