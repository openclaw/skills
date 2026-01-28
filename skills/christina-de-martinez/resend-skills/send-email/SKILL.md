---
name: send-email
description: Use when sending transactional emails (welcome messages, order confirmations, password resets, receipts), notifications, or bulk emails via Resend API.
---

# Send Email with Resend

## Overview

Resend provides two endpoints for sending emails:

| Approach | Endpoint | Use Case |
|----------|----------|----------|
| **Single** | `POST /emails` | Individual transactional emails, emails with attachments, scheduled sends |
| **Batch** | `POST /emails/batch` | Multiple distinct emails in one request (max 100), bulk notifications |

**Choose batch when:**
- Sending 2+ distinct emails at once
- Reducing API calls is important (by default, rate limit is 2 requests per second)
- No attachments or scheduling needed

**Choose single when:**
- Sending one email
- Email needs attachments
- Email needs to be scheduled
- Different recipients need different timing

## Quick Start

1. **Detect project language** from config files (package.json, requirements.txt, go.mod, etc.)
2. **Install SDK** (preferred) or use cURL - See [references/installation.md](references/installation.md)
3. **Choose single or batch** based on the decision matrix above
4. **Implement best practices** - Idempotency keys, error handling, retries

## Best Practices (Critical for Production)

Always implement these for production email sending. See [references/best-practices.md](references/best-practices.md) for complete implementations.

### Idempotency Keys

Prevent duplicate emails when retrying failed requests.

| Key Facts | |
|-----------|---|
| **Format (single)** | `<event-type>/<entity-id>` (e.g., `welcome-email/user-123`) |
| **Format (batch)** | `batch-<event-type>/<batch-id>` (e.g., `batch-orders/batch-456`) |
| **Expiration** | 24 hours |
| **Max length** | 256 characters |
| **Duplicate payload** | Returns original response without resending |
| **Different payload** | Returns 409 error |

### Error Handling

| Code | Action |
|------|--------|
| 400, 422 | Fix request parameters, don't retry |
| 401, 403 | Check API key / verify domain, don't retry |
| 409 | Idempotency conflict - use new key or fix payload |
| 429 | Rate limited - retry with exponential backoff (by default, rate limit is 2 requests/second) |
| 500 | Server error - retry with exponential backoff |

### Retry Strategy

- **Backoff:** Exponential (1s, 2s, 4s...)
- **Max retries:** 3-5 for most use cases
- **Only retry:** 429 (rate limit) and 500 (server error)
- **Always use:** Idempotency keys when retrying

## Single Email

**Endpoint:** `POST /emails` (prefer SDK over cURL)

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | string | Sender address. Format: `"Name <email@domain.com>"` |
| `to` | string[] | Recipient addresses (max 50) |
| `subject` | string | Email subject line |
| `html` or `text` | string | Email body content |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cc` | string[] | CC recipients |
| `bcc` | string[] | BCC recipients |
| `reply_to`* | string[] | Reply-to addresses |
| `scheduled_at`* | string | Schedule send time (ISO 8601) |
| `attachments` | array | File attachments (max 40MB total) |
| `tags` | array | Key/value pairs for tracking (see [Tags](#tags)) |
| `headers` | object | Custom headers |

*Parameter naming varies by SDK (e.g., `replyTo` in Node.js, `reply_to` in Python).

### Minimal Example (Node.js)

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send(
  {
    from: 'Acme <onboarding@resend.dev>',
    to: ['delivered@resend.dev'],
    subject: 'Hello World',
    html: '<p>Email body here</p>',
  },
  { idempotencyKey: `welcome-email/${userId}` }
);

if (error) {
  console.error('Failed:', error.message);
  return;
}
console.log('Sent:', data.id);
```

See [references/single-email-examples.md](references/single-email-examples.md) for all SDK implementations with error handling and retry logic.

## Batch Email

**Endpoint:** `POST /emails/batch` (but prefer SDK over cURL)

### Limitations

- **No attachments** - Use single sends for emails with attachments
- **No scheduling** - Use single sends for scheduled emails
- **Atomic** - If one email fails validation, the entire batch fails
- **Max 100 emails** per request
- **Max 50 recipients** per individual email in the batch

### Pre-validation

Since the entire batch fails on any validation error, validate all emails before sending:
- Check required fields (from, to, subject, html/text)
- Validate email formats
- Ensure batch size <= 100

### Minimal Example (Node.js)

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.batch.send(
  [
    {
      from: 'Acme <notifications@acme.com>',
      to: ['delivered@resend.dev'],
      subject: 'Order Shipped',
      html: '<p>Your order has shipped!</p>',
    },
    {
      from: 'Acme <notifications@acme.com>',
      to: ['delivered@resend.dev'],
      subject: 'Order Confirmed',
      html: '<p>Your order is confirmed!</p>',
    },
  ],
  { idempotencyKey: `batch-orders/${batchId}` }
);

if (error) {
  console.error('Batch failed:', error.message);
  return;
}
console.log('Sent:', data.map(e => e.id));
```

See [references/batch-email-examples.md](references/batch-email-examples.md) for all SDK implementations with validation, error handling, and retry logic.

## Large Batches (100+ Emails)

For sends larger than 100 emails, chunk into multiple batch requests:

1. **Split into chunks** of 100 emails each
2. **Use unique idempotency keys** per chunk: `<batch-prefix>/chunk-<index>`
3. **Send chunks in parallel** for better throughput
4. **Track results** per chunk to handle partial failures

See [references/batch-email-examples.md](references/batch-email-examples.md) for complete chunking implementations.

## Deliverability

Follow these practices to maximize inbox placement.

For more help with deliverability, install the email-best-practices skill with `npx skills add resend/email-best-practices`.

### Required

| Practice | Why |
|----------|-----|
| **Valid SPF, DKIM, DMARC record** | authenticate the email and prevent spoofing |
| **Links match sending domain** | If sending from `@acme.com`, link to `https://acme.com` - mismatched domains trigger spam filters |
| **Include plain text version** | Use both `html` and `text` parameters for accessibility and deliverability (Resend generates a plain text version if not provided) |
| **Avoid "no-reply" addresses** | Use real addresses (e.g., `support@`) - improves trust signals |
| **Keep body under 102KB** | Gmail clips larger messages |

### Recommended

| Practice | Why |
|----------|-----|
| **Use subdomains** | Send transactional from `notifications.acme.com`, marketing from `mail.acme.com` - protects reputation |
| **Disable tracking for transactional** | Open/click tracking can trigger spam filters for password resets, receipts, etc. |

## Tracking (Opens & Clicks)

Tracking is configured at the **domain level** in the Resend dashboard, not per-email.

| Setting | How it works | Recommendation |
|---------|--------------|----------------|
| **Open tracking** | Inserts 1x1 transparent pixel | Disable for transactional emails - can hurt deliverability |
| **Click tracking** | Rewrites links through redirect | Disable for sensitive emails (password resets, security alerts) |

**When to enable tracking:**
- Marketing emails where engagement metrics matter
- Newsletters and announcements

**When to disable tracking:**
- Transactional emails (receipts, confirmations, password resets)
- Security-sensitive emails
- When maximizing deliverability is priority

Configure via dashboard: Domain → Configuration → Click/Open Tracking

## Webhooks (Event Notifications)

Track email delivery status in real-time using webhooks. Resend sends HTTP POST requests to your endpoint when events occur.

| Event | When to use |
|-------|-------------|
| `email.delivered` | Confirm successful delivery |
| `email.bounced` | Remove from mailing list, alert user |
| `email.complained` | Unsubscribe user (spam complaint) |
| `email.opened` / `email.clicked` | Track engagement (marketing only) |

**CRITICAL: Always verify webhook signatures.** Without verification, attackers can send fake events to your endpoint.

See [references/webhooks.md](references/webhooks.md) for setup, signature verification code, and all event types.

## Tags

Tags are key/value pairs that help you track and filter emails.

```typescript
tags: [
  { name: 'user_id', value: 'usr_123' },
  { name: 'email_type', value: 'welcome' },
  { name: 'plan', value: 'enterprise' }
]
```

**Use cases:**
- Associate emails with customers in your system
- Categorize by email type (welcome, receipt, password-reset)
- Filter emails in the Resend dashboard
- Correlate webhook events back to your application

**Constraints:** Tag names and values can only contain ASCII letters, numbers, underscores, or dashes. Max 256 characters each.

## Templates

Use pre-built templates instead of sending HTML with each request.

```typescript
const { data, error } = await resend.emails.send({
  from: 'Acme <hello@acme.com>',
  to: ['delivered@resend.dev'],
  subject: 'Welcome!',
  template: {
    id: 'tmpl_abc123',
    variables: {
      USER_NAME: 'John',      // Case-sensitive!
      ORDER_TOTAL: '$99.00'
    }
  }
});
```

**IMPORTANT:** Variable names are **case-sensitive** and must match exactly as defined in the template editor. `USER_NAME` ≠ `user_name`.

| Fact | Detail |
|------|--------|
| **Max variables** | 20 per template |
| **Reserved names** | `FIRST_NAME`, `LAST_NAME`, `EMAIL`, `RESEND_UNSUBSCRIBE_URL`, `contact`, `this` |
| **Fallback values** | Optional - if not set and variable missing, send fails |
| **Can't combine with** | `html`, `text`, or `react` parameters |

Templates must be **published** in the dashboard before use. Draft templates won't work.

## Testing

**WARNING: Never test with fake addresses at real email providers.**

Using addresses like `test@gmail.com`, `example@outlook.com`, or `fake@yahoo.com` will:
- **Bounce** - These addresses don't exist
- **Destroy your sender reputation** - High bounce rates trigger spam filters
- **Get your domain blocklisted** - Providers flag domains with high bounce rates

### Safe Testing Options

| Method | Address | Result |
|--------|---------|--------|
| **Delivered** | `delivered@resend.dev` | Simulates successful delivery |
| **Bounced** | `bounced@resend.dev` | Simulates hard bounce |
| **Complained** | `complained@resend.dev` | Simulates spam complaint |
| **Your own email** | Your actual address | Real delivery test |

**For development:** Use the `resend.dev` test addresses to simulate different scenarios without affecting your reputation.

**For staging:** Send to real addresses you control (team members, test accounts you own).

## Domain Warm-up

New domains must gradually increase sending volume to establish reputation.

**Why it matters:** Sudden high volume from a new domain triggers spam filters. ISPs expect gradual growth.

### Recommended Schedule

**Existing domain**

| Day | Messages per day    | Messages per hour   |
|-----|---------------------|---------------------|
| 1   | Up to 1,000 emails  | 100 Maximum         |
| 2   | Up to 2,500 emails  | 300 Maximum         |
| 3   | Up to 5,000 emails  | 600 Maximum         |
| 4   | Up to 5,000 emails  | 800 Maximum         |
| 5   | Up to 7,500 emails  | 1,000 Maximum       |
| 6   | Up to 7,500 emails  | 1,500 Maximum       |
| 7   | Up to 10,000 emails | 2,000 Maximum       |

**New domain**

| Day | Messages per day    | Messages per hour   |
|-----|---------------------|---------------------|
| 1   | Up to 150 emails    |                    |
| 2   | Up to 250 emails    |                    |
| 3   | Up to 400 emails    |                    |
| 4   | Up to 700 emails    | 50 Maximum         |
| 5   | Up to 1,000 emails  | 75 Maximum         |
| 6   | Up to 1,500 emails  | 100 Maximum        |
| 7   | Up to 2,000 emails  | 150 Maximum        |

### Monitor These Metrics

| Metric | Target | Action if exceeded |
|--------|--------|-------------------|
| **Bounce rate** | < 4% | Slow down, clean list |
| **Spam complaint rate** | < 0.08% | Slow down, review content |

**Don't use third-party warm-up services.** Focus on sending relevant content to real, engaged recipients.

## Suppression List

Resend automatically manages a suppression list of addresses that should not receive emails.

**Addresses are added when:**
- Email hard bounces (address doesn't exist)
- Recipient marks email as spam
- You manually add them via dashboard

**What happens:** Resend won't attempt delivery to suppressed addresses. The `email.suppressed` webhook event fires instead.

**Why this matters:** Continuing to send to bounced/complained addresses destroys your reputation. The suppression list protects you automatically.

**Management:** View and manage suppressed addresses in the Resend dashboard under Suppressions.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Retrying without idempotency key | Always include idempotency key - prevents duplicate sends on retry |
| Using batch for emails with attachments | Batch doesn't support attachments - use single sends instead |
| Not validating batch before send | Validate all emails first - one invalid email fails the entire batch |
| Retrying 400/422 errors | These are validation errors - fix the request, don't retry |
| Same idempotency key, different payload | Returns 409 error - use unique key per unique email content |
| Tracking enabled for transactional emails | Disable open/click tracking for password resets, receipts - hurts deliverability |
| Using "no-reply" sender address | Use real address like `support@` - improves trust signals with email providers |
| Not verifying webhook signatures | Always verify - attackers can send fake events to your endpoint |
| Testing with fake emails (test@gmail.com) | Use `delivered@resend.dev` - fake addresses bounce and hurt reputation |
| Template variable name mismatch | Variable names are case-sensitive - `USER_NAME` ≠ `user_name` |
| Sending high volume from new domain | Warm up gradually - sudden spikes trigger spam filters |

## Notes

- The `from` address must use a verified domain
- If the sending address cannot receive replies, set the `reply_to` parameter to a valid address.
- Store API key in `RESEND_API_KEY` environment variable
- Node.js SDK supports `react` parameter for React Email components
- Resend returns `error`, `data`, `headers` in the response.
- Data returns `{ id: "email-id" }` on success (single) or array of IDs (batch)
- For marketing campaigns to large lists, use Resend Broadcasts instead