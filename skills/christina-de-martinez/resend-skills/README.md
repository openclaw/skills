```
 ____  _____ ____  _____ _   _ ____        ____  _  _____ _     _     ____
|  _ \| ____/ ___|| ____| \ | |  _ \      / ___|| |/ /_ _| |   | |   / ___|
| |_) |  _| \___ \|  _| |  \| | | | |_____\___ \| ' / | || |   | |   \___ \
|  _ <| |___ ___) | |___| |\  | |_| |_____|___) | . \ | || |___| |___ ___) |
|_| \_\_____|____/|_____|_| \_|____/      |____/|_|\_\___|_____|_____|____/
```

# Resend Skills

A collection of skills for AI coding agents following the Agent Skills format. These skills enable AI agents to send emails using the [Resend](https://resend.com) API.

## Available Skills

### [`send-email`](./send-email)
Send emails using the Resend API - single or batch. Supports transactional emails, notifications, and bulk sending (up to 100 emails per batch). Includes best practices for idempotency keys, error handling, and retry logic.

## Installation

```bash
npx skills add resend/resend-skills
```

## Usage

Skills are automatically activated when relevant tasks are detected. Example prompts:

- "Send a welcome email to new users"
- "Send batch notifications to all order customers"
- "Schedule a newsletter for tomorrow at 9am"

## Supported SDKs

- Node.js / TypeScript
- Python
- Go
- Ruby
- PHP
- Rust
- Java
- .NET
- cURL
- SMTP

## Prerequisites

- A Resend account with a verified domain
- API key stored in `RESEND_API_KEY` environment variable

Get your API key at [resend.com/api-keys](https://resend.com/api-keys)

## License

MIT
