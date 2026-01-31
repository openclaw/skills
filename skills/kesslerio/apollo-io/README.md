# Apollo.io Skill for OpenClaw

Sales intelligence and lead discovery via [Apollo.io](https://apollo.io)'s REST API. Search 210M+ contacts and 35M+ companies directly from your OpenClaw workspace.

## Features

- 🔍 **People Search** — Find prospects by job title, company, keywords
- 👤 **Person Enrichment** — Get contact details from email or LinkedIn URL
- 🏢 **Company Search** — Discover companies by industry, size, location
- 📊 **Company Enrichment** — Get company intel from domain or name

## Installation

1. Clone/copy this skill to your OpenClaw `skills/` directory
2. Get your API key from [Apollo Settings → API](https://apollo.io/settings/api)
3. Set the environment variable:
   ```bash
   export APOLLO_API_KEY=your_key_here
   ```

## Usage

### Command Line

```bash
# Search for VP Engineering at Stripe
python scripts/search_people.py --title "VP Engineering" --company Stripe

# Enrich a contact from email
python scripts/enrich_person.py --email john@example.com

# Search for healthcare companies
python scripts/search_companies.py --industry "Healthcare" --size "51-200"

# Enrich company from domain
python scripts/enrich_company.py --domain stripe.com
```

### In OpenClaw

Once installed, just ask naturally:

- "Find me VP Engineering contacts at Stripe"
- "Enrich this email: john@example.com"
- "Look up company info for stripe.com"
- "Search for healthcare companies with 50-200 employees"

## API Reference

- [Apollo API Documentation](https://docs.apollo.io/)
- Base URL: `https://api.apollo.io/v1`
- Auth: `X-Api-Key` header

## Requirements

- Python 3.8+
- `requests` library
- Apollo.io API key (paid plan required for API access)

## License

Apache 2.0 — see [LICENSE](LICENSE)
