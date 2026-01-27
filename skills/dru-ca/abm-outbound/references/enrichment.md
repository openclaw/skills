# Enrichment Reference

## LinkedIn Scraping (Apify)

```bash
curl -X POST "https://api.apify.com/v2/acts/harvestapi~linkedin-profile-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profileUrls": ["https://linkedin.com/in/username"]}'
```

**Returns:**
| Field | Description |
|-------|-------------|
| `firstName` | First name |
| `lastName` | Last name |
| `headline` | Job title/tagline |
| `company` | Current company |
| `location` | City, State |

## Apollo: Email & Phone Enrichment

```bash
curl -X POST "https://api.apollo.io/api/v1/people/bulk_match" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "reveal_personal_emails": true,
    "reveal_phone_number": true,
    "details": [{
      "first_name": "John",
      "last_name": "Doe",
      "organization_name": "Acme Corp",
      "linkedin_url": "https://linkedin.com/in/johndoe"
    }]
  }'
```

**Returns:**
| Field | Description |
|-------|-------------|
| `email` | Work email |
| `phone_numbers` | Array of phones |
| `title` | Job title |

**Tips:**
- Up to 10 people per call
- Include `linkedin_url` for better match accuracy
- Free tier: email only; paid plans: phone numbers

## Skip Trace (Mailing Address)

```bash
curl -X POST "https://api.apify.com/v2/acts/one-api~skip-trace/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": ["John Doe"]}'
```

**Returns:**
| Field | Description |
|-------|-------------|
| `address.street` | Street address |
| `address.city` | City |
| `address.state` | State |
| `address.postalCode` | ZIP/Postal code |
| `phones[]` | Additional phones |
| `emails[]` | Additional emails |

**Cost:** ~$0.007 per lookup

**Important:** Returns HOME addresses from public records. Verify state matches LinkedIn location.

## Address Verification

```python
def is_address_valid(skip_trace_state, linkedin_state):
    """Address is valid if state matches LinkedIn location."""
    return normalize_state(skip_trace_state) == normalize_state(linkedin_state)
```

If states don't match, the person may have moved — flag for review or skip.
