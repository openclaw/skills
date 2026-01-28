---
name: dex-crm
description: |
  Manage Dex personal CRM (getdex.com) contacts, notes, and reminders.
  Use when you need to: (1) Search or browse contacts, (2) Add notes about people,
  (3) Create or check reminders, (4) Look up contact details (phone, email, birthday).
  Requires DEX_API_KEY environment variable.
---

# Dex Personal CRM

Manage your Dex CRM directly from Clawdbot. Search contacts, add notes, manage reminders.

## Authentication

Set `DEX_API_KEY` in gateway config env vars.

## API Base

- **Base URL:** `https://api.getdex.com/api/rest`
- **Headers:** `Content-Type: application/json` and `x-hasura-dex-api-key: $DEX_API_KEY`

## Quick Reference

### Contacts

```bash
# List contacts (paginated)
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/contacts?limit=10&offset=0"

# Get contact by ID
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/contacts/{contactId}"

# Search contact by email
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/search/contacts?email=someone@example.com"

# Create contact
curl -s -X POST -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"first_name":"John","last_name":"Doe","emails":["john@example.com"]}' \
  "https://api.getdex.com/api/rest/contacts"

# Update contact
curl -s -X PUT -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"job_title":"CEO"}' \
  "https://api.getdex.com/api/rest/contacts/{contactId}"

# Delete contact
curl -s -X DELETE -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/contacts/{contactId}"
```

### Notes (Timeline Items)

```bash
# List notes
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/timeline_items?limit=10&offset=0"

# Notes for a contact
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/timeline_items/contacts/{contactId}"

# Create note
curl -s -X POST -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"note":"Met for coffee, discussed project","contact_ids":["contact-uuid"],"event_time":"2026-01-27T12:00:00Z"}' \
  "https://api.getdex.com/api/rest/timeline_items"

# Update note
curl -s -X PUT -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"note":"Updated note text"}' \
  "https://api.getdex.com/api/rest/timeline_items/{noteId}"

# Delete note
curl -s -X DELETE -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/timeline_items/{noteId}"
```

### Reminders

```bash
# List reminders
curl -s -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/reminders?limit=10&offset=0"

# Create reminder
curl -s -X POST -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"body":"Follow up on proposal","due_at_date":"2026-02-01","contact_ids":["contact-uuid"]}' \
  "https://api.getdex.com/api/rest/reminders"

# Update reminder
curl -s -X PUT -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  -d '{"is_complete":true}' \
  "https://api.getdex.com/api/rest/reminders/{reminderId}"

# Delete reminder
curl -s -X DELETE -H "Content-Type: application/json" \
  -H "x-hasura-dex-api-key: $DEX_API_KEY" \
  "https://api.getdex.com/api/rest/reminders/{reminderId}"
```

## Contact Fields

- `first_name`, `last_name`, `job_title`, `description`
- `emails` (array of `{email}`)
- `phones` (array of `{phone_number}`)
- `education`, `website`, `linkedin`, `facebook`, `twitter`, `instagram`, `telegram`
- `birthday`, `image_url`
- `last_seen_at`, `next_reminder_at`
- `is_archived`, `created_at`, `updated_at`

## Searching Contacts

The API only supports search by email. For name-based search, fetch contacts in batches and filter locally. Use a reasonable limit (50-100) for browsing.

## Notes

- Always confirm before creating, updating, or deleting contacts/notes/reminders
- Contact search by name requires local filtering (API only supports email search)
- Use pagination (limit/offset) for large result sets
- The `event_time` field on notes is when the interaction happened, not when the note was created
