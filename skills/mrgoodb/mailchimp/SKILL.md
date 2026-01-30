---
name: mailchimp
description: Manage email marketing campaigns, audiences, and automations via Mailchimp API.
metadata: {"clawdbot":{"emoji":"🐵","requires":{"env":["MAILCHIMP_API_KEY","MAILCHIMP_SERVER"]}}}
---

# Mailchimp

Email marketing automation.

## Environment

```bash
export MAILCHIMP_API_KEY="xxxxxxxxxx-us1"
export MAILCHIMP_SERVER="us1"  # From API key suffix
```

## List Audiences

```bash
curl "https://$MAILCHIMP_SERVER.api.mailchimp.com/3.0/lists" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

## Add Subscriber

```bash
curl -X POST "https://$MAILCHIMP_SERVER.api.mailchimp.com/3.0/lists/{list_id}/members" \
  -u "anystring:$MAILCHIMP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "user@example.com",
    "status": "subscribed",
    "merge_fields": {"FNAME": "John", "LNAME": "Doe"}
  }'
```

## List Campaigns

```bash
curl "https://$MAILCHIMP_SERVER.api.mailchimp.com/3.0/campaigns" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

## Get Campaign Stats

```bash
curl "https://$MAILCHIMP_SERVER.api.mailchimp.com/3.0/reports/{campaign_id}" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

## Send Campaign

```bash
curl -X POST "https://$MAILCHIMP_SERVER.api.mailchimp.com/3.0/campaigns/{campaign_id}/actions/send" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

## Links
- Dashboard: https://mailchimp.com
- Docs: https://mailchimp.com/developer/
