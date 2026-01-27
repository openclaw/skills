# Scribeless API Reference

**Documentation:** [docs.scribeless.co](https://docs.scribeless.co)

**Platform:** [platform.scribeless.co](https://platform.scribeless.co)

## Getting Started

1. Sign into [platform.scribeless.co](https://platform.scribeless.co) and setup your team
2. Create an API key: Settings > API Keys > Create API Key
3. Create a campaign in the platform to get a `campaignId`

## Authentication

The Scribeless API uses the `X-API-Key` header for authentication.

```bash
curl -X POST "https://platform.scribeless.co/api/recipients" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '...'
```

Generate your API key at: [platform.scribeless.co/settings/teams/api-keys](https://platform.scribeless.co/settings/teams/api-keys)

> ⚠️ **Warning:** Once you confirm you have securely copied an API Key, there is no way of viewing that key again. A new key will need to be created if the secret is lost.

### Error Responses

| Code | Meaning |
|------|---------|
| 401 | API key missing, malformed, or invalid |
| 503 | Unexpected traffic spike — usually resolves within 5 minutes |
| 5XX | Server error — contact support |

## Endpoints

### Create Recipients

```
POST https://platform.scribeless.co/api/recipients
```

Add recipients to an existing campaign.

#### Request Body

```json
{
  "campaignId": "CAMPAIGN_ID",
  "data": {
    "title": "Mr",
    "firstName": "Joe",
    "lastName": "Blogs",
    "company": "Blogs Inc.",
    "address": {
      "address1": "123 Blogs St",
      "address2": "",
      "address3": "",
      "city": "Bristol",
      "state": "Bristol",
      "postalCode": "AB123CD",
      "country": "GB"
    },
    "variables": {
      "custom1": "This is a personalized first sentence",
      "custom2": "www.scribeless.co"
    }
  }
}
```

#### Fields

| Field | Description |
|-------|-------------|
| `campaignId` | Campaign ID from the Scribeless platform (required) |
| `data.title` | Salutation (Mr, Ms, Dr, etc.) |
| `data.firstName` | First name |
| `data.lastName` | Last name |
| `data.company` | Company name |
| `data.address.address1` | Street address line 1 |
| `data.address.address2` | Street address line 2 |
| `data.address.address3` | Street address line 3 |
| `data.address.city` | City |
| `data.address.state` | State/Province/County |
| `data.address.postalCode` | Postal/ZIP code |
| `data.address.country` | Country code (GB, US, etc.) |
| `data.variables` | Custom variables for personalization |

#### Example: Single Recipient

```bash
curl --location 'https://platform.scribeless.co/api/recipients' \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "campaignId": "CAMPAIGN_ID",
    "data": {
      "title": "Mr",
      "firstName": "Joe",
      "lastName": "Blogs",
      "company": "Blogs Inc.",
      "address": {
        "address1": "123 Blogs St",
        "city": "Bristol",
        "state": "Bristol",
        "postalCode": "AB123CD",
        "country": "GB"
      },
      "variables": {
        "custom1": "This is a personalized first sentence",
        "custom2": "www.scribeless.co"
      }
    }
  }'
```

## Workflow

1. **Create campaign** in the Scribeless platform UI
2. **Get campaign ID** from the campaign settings
3. **Add recipients** via API with personalization variables
4. **Review & send** in the platform

## Personalization Variables

Use `variables` to pass custom data for each recipient. These map to merge fields in your letter template.

Common use cases:
- `custom1` — Personalized opening sentence
- `custom2` — Custom CTA or URL
- Any key/value pair for template merge fields

## Support

Email: [team@scribeless.co](mailto:team@scribeless.co)
