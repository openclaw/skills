---
name: resend
description: Use when working with Resend email platform - routes to specific sub-skills for sending, receiving, audiences, or broadcasts.
license: MIT
metadata:
    author: resend
    version: "1.1.0"
---

# Resend

## Overview

Resend is an email platform for developers. This skill routes to feature-specific sub-skills.

## Sub-Skills

| Feature | Skill | Use When |
|---------|-------|----------|
| **Sending emails** | `send-email` | Transactional emails, notifications, batch sends |
| **Receiving emails** | `resend-inbound` | Processing inbound emails, webhooks for received mail, attachments |

## Quick Routing

**Need to send emails?** Use `send-email` skill
- Single or batch transactional emails
- Attachments, scheduling, templates
- Delivery webhooks (bounced, delivered, opened)

**Need to receive emails?** Use `resend-inbound` skill
- Setting up inbound domain (MX records)
- Processing `email.received` webhooks
- Retrieving email content and attachments
- Forwarding received emails

## Common Setup

### API Key

Store in environment variable:
```bash
export RESEND_API_KEY=re_xxxxxxxxx
```

### SDK Installation

See `send-email` skill for installation instructions across all supported languages.

## Resources

- [Resend Documentation](https://resend.com/docs)
- [API Reference](https://resend.com/docs/api-reference)
- [Dashboard](https://resend.com/emails)
