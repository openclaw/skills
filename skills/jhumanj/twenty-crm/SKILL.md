---
name: twenty-crm
description: Interact with Twenty CRM (self-hosted) via REST/GraphQL.
metadata: {"clawdbot":{"emoji":"🗂️","os":["darwin","linux"]}}
---

# Twenty CRM

Interact with your self-hosted Twenty instance via REST and GraphQL.

## Config

Create `config/twenty.env` (example at `config/twenty.env.example`):

- `TWENTY_BASE_URL` (e.g. `https://crm.example.com` or `http://localhost:3000`)
- `TWENTY_API_KEY` (Bearer token)

Scripts load this file automatically.

## Commands

### Low-level helpers

- REST GET: `skills/twenty-crm/scripts/twenty-rest-get.sh "/companies" 'filter={"name":{"ilike":"%acme%"}}&limit=10'`
- REST POST: `skills/twenty-crm/scripts/twenty-rest-post.sh "/companies" '{"name":"Acme"}'`
- REST PATCH: `skills/twenty-crm/scripts/twenty-rest-patch.sh "/companies/<id>" '{"employees":550}'`
- REST DELETE: `skills/twenty-crm/scripts/twenty-rest-delete.sh "/companies/<id>"`

- GraphQL: `skills/twenty-crm/scripts/twenty-graphql.sh 'query { companies(limit: 5) { totalCount } }'`

### Common objects (examples)

- Create company: `skills/twenty-crm/scripts/twenty-create-company.sh "Acme" "acme.com" 500`
- Find companies by name: `skills/twenty-crm/scripts/twenty-find-companies.sh "acme" 10`

## Notes

- Twenty supports both REST (`/rest/...`) and GraphQL (`/graphql`).
- Object names/endpoints can differ depending on your workspace metadata and Twenty version.
- Auth tokens can be short-lived depending on your setup; refresh if you get `401`.
