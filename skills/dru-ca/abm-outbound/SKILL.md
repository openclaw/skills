---
name: ABM Outbound
description: Multi-channel ABM automation that turns LinkedIn URLs into coordinated outbound campaigns. Scrapes profiles, enriches with Apollo (email + phone), gets mailing addresses via Skip Trace, then orchestrates email sequences, LinkedIn touches, and handwritten letters via Scribeless. The secret weapon for standing out in crowded inboxes.
---

# ABM Outbound

Turn LinkedIn prospect lists into multi-channel outbound: email sequences, LinkedIn touches, and handwritten letters.

## Prerequisites

| Service | Purpose | Sign Up |
|---------|---------|---------|
| **Apify** | LinkedIn scraping, Skip Trace | [apify.com](https://apify.com) |
| **Apollo** | Email & phone enrichment | [apollo.io](https://apollo.io) |
| **Scribeless** | Handwritten letters | [platform.scribeless.co](https://platform.scribeless.co) |
| **Instantly** *(optional)* | Dedicated cold email | [instantly.ai](https://instantly.ai) |

```bash
export APIFY_API_KEY="your_key"
export APOLLO_API_KEY="your_key"
export SCRIBELESS_API_KEY="your_key"
```

## Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. INPUT   │───▶│  2. SCRAPE  │───▶│  3. ENRICH  │───▶│  4. ADDRESS │───▶│ 5. OUTREACH │
│  LinkedIn   │    │  Profiles   │    │ Email/Phone │    │ Skip Trace  │    │             │
│    URLs     │    │             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
   Your list          Apify             Apollo            Apify PFI        Email +
                                                                          LinkedIn +
                                                                          Scribeless
```

## Step 1: Gather LinkedIn URLs

Provide a list of LinkedIn profile URLs from:
- LinkedIn Sales Navigator exports
- LinkedIn search scrapers
- CRM exports
- Manual prospecting

```csv
linkedin_url
https://linkedin.com/in/johndoe
https://linkedin.com/in/janesmith
```

## Step 2: Scrape LinkedIn Profiles

```bash
curl -X POST "https://api.apify.com/v2/acts/harvestapi~linkedin-profile-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profileUrls": [
      "https://linkedin.com/in/johndoe",
      "https://linkedin.com/in/janesmith"
    ]
  }'
```

**Returns:** First name, last name, company, title, location.

## Step 3: Enrich with Apollo (Email & Phone)

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

**Returns:** Work email, phone numbers.

## Step 4: Get Mailing Address (Skip Trace)

```bash
curl -X POST "https://api.apify.com/v2/acts/one-api~skip-trace/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": ["John Doe"]}'
```

**Returns:** Street address, city, state, postal code.

**Important:** Verify Skip Trace state matches LinkedIn location.

## Step 5: Multi-Channel Outreach

### 5a: Email Sequence

**Option 1: Apollo Sequences (Recommended)**
```bash
curl -X POST "https://api.apollo.io/api/v1/emailer_campaigns/add_contact_ids" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "emailer_campaign_id": "YOUR_SEQUENCE_ID",
    "contact_ids": ["CONTACT_ID_1", "CONTACT_ID_2"],
    "send_email_from_email_account_id": "YOUR_EMAIL_ACCOUNT_ID"
  }'
```

**Option 2: Instantly.ai**
```bash
curl -X POST "https://api.instantly.ai/api/v1/lead/add" \
  -H "Authorization: Bearer $INSTANTLY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "YOUR_CAMPAIGN_ID",
    "email": "john@acme.com",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp",
    "personalization": "Saw Acme just expanded to UK"
  }'
```

**Option 3: CSV Upload**
```csv
email,first_name,last_name,company,title,phone,personalization
john@acme.com,John,Doe,Acme Corp,VP Marketing,555-1234,Saw Acme just expanded to UK
```

### 5b: LinkedIn Sequence
- Day 1: View profile
- Day 2: Connection request with personalized note
- Day 4: Follow-up message if connected
- Day 7: Engage with their content

### 5c: Handwritten Letter (Scribeless)

Create campaign at [platform.scribeless.co](https://platform.scribeless.co), then add recipients:

```bash
curl -X POST "https://platform.scribeless.co/api/recipients" \
  -H "X-API-Key: $SCRIBELESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "campaignId": "YOUR_CAMPAIGN_ID",
    "data": {
      "firstName": "John",
      "lastName": "Doe",
      "company": "Acme Corp",
      "address": {
        "address1": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postalCode": "94102",
        "country": "US"
      },
      "variables": {
        "custom1": "Saw Acme just expanded to the UK — congrats!"
      }
    }
  }'
```

See [references/scribeless-api.md](references/scribeless-api.md) for full API details.

## Coordinated Timing

| Day | Email | LinkedIn | Letter |
|-----|-------|----------|--------|
| 1 | — | View profile | Letter sent |
| 3 | — | Connection request | — |
| 5 | "Got my note?" | — | Letter arrives |
| 7 | Value email | Message if connected | — |
| 10 | Case study | — | — |
| 14 | Break-up | Engage content | — |

**The play:** Letter lands → Email references it → LinkedIn reinforces.

## Complete Workflow

```python
# 1. Start with LinkedIn URLs
linkedin_urls = load_csv("prospects.csv")

# 2. Scrape profiles
profiles = apify_linkedin_scrape(linkedin_urls)

# 3. Enrich with Apollo
for profile in profiles:
    enriched = apollo_bulk_match(profile)
    profile['email'] = enriched['email']
    profile['phone'] = enriched['phone']

# 4. Get mailing addresses
for profile in profiles:
    address = skip_trace(profile['name'])
    if address['state'] == profile['linkedin_state']:
        profile['address'] = address
        profile['mailable'] = True

# 5. Push to channels
push_to_email_tool(profiles)
push_to_scribeless(profiles, campaign_id)
export_for_linkedin(profiles)
```

## Output Format

```csv
first_name,last_name,email,phone,company,title,address1,city,state,postal,country,linkedin,mailable
John,Doe,john@acme.com,555-1234,Acme Corp,VP Marketing,123 Main St,San Francisco,CA,94102,US,linkedin.com/in/johndoe,TRUE
```

## Best Practices

1. **Verify addresses** — Skip Trace state should match LinkedIn location
2. **Personalize everything** — Company news, job changes, shared connections
3. **Coordinate timing** — Letter lands before "did you get my note?" email
4. **Start small** — Test with 20-50 prospects before scaling
5. **Track by channel** — Know which channel drives replies
