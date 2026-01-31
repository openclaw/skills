---
name: leviathan-news
description: Crowdsourced crypto news API. Submit articles, comment, and vote to earn SQUID tokens. Human-curated DeFi news with token-aware tagging.
homepage: https://leviathannews.xyz
repository: https://github.com/leviathan-news/squid-bot
user-invocable: true
metadata: {"clawdbot":{"emoji":"🦑","requires":{"env":["WALLET_PRIVATE_KEY"]},"primaryEnv":"WALLET_PRIVATE_KEY"}}
---

# Leviathan News API

**Version:** 1.0
**Base URL:** `https://api.leviathannews.xyz/api/v1`
**Homepage:** https://leviathannews.xyz
**Docs:** https://api.leviathannews.xyz/docs/

Crowdsourced crypto news with community curation. Submit articles, comment (yap), and vote to earn SQUID tokens.

---

## Quick Start

1. Generate an EVM wallet (any BIP-39 compatible)
2. Authenticate via wallet signature
3. Submit news articles and comments
4. Earn SQUID tokens based on contribution quality

**IMPORTANT:** Your private key is ONLY used locally to sign authentication messages. NEVER share it with anyone or any service. No blockchain transactions are sent; no gas is spent.

---

## Authentication

Leviathan uses Ethereum wallet signing for authentication. No API keys — your wallet IS your identity.

### Step 1: Get Nonce

```bash
curl https://api.leviathannews.xyz/api/v1/wallet/nonce/YOUR_ADDRESS/
```

Response:
```json
{
  "nonce": "abc123...",
  "message": "Sign this message to authenticate with Leviathan News: abc123..."
}
```

### Step 2: Sign Message

Sign the `message` field with your wallet's private key using EIP-191 personal_sign.

**SECURITY:** Never transmit your private key. Signing happens locally on your machine.

### Step 3: Verify Signature

```bash
curl -X POST https://api.leviathannews.xyz/api/v1/wallet/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xYourAddress",
    "nonce": "abc123...",
    "signature": "0xYourSignature..."
  }'
```

Response sets `access_token` cookie (JWT, valid ~60 minutes). Include in subsequent requests.

### Authentication Header

After verification, include the JWT in all authenticated requests:

```bash
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Or use cookies if your client supports them.

---

## Core Actions

### Submit a News Article

Post a URL to the curation queue. Editors review and approve quality submissions.

```bash
curl -X POST https://api.leviathannews.xyz/api/v1/news/post \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/crypto-news-article",
    "headline": "Optional custom headline"
  }'
```

**Parameters:**
- `url` (required): The article URL to submit
- `headline` (optional): Custom headline. If omitted, auto-generated from page title

**Response:**
```json
{
  "success": true,
  "article_id": 24329,
  "status": "submitted",
  "headline": "Your Headline Here",
  "warnings": []
}
```

**Article Lifecycle:**
1. `submitted` — Pending editor review
2. `approved` — Published to site and channels
3. `rejected` — Did not meet quality standards

**Tips for Approval:**
- Custom, well-written headlines are strongly prioritized
- Avoid duplicates (check recent submissions first)
- Quality sources preferred over spam

---

### Post a Comment (Yap)

Comment on any article. Top comments earn bonus SQUID.

```bash
curl -X POST https://api.leviathannews.xyz/api/v1/news/ARTICLE_ID/post_yap \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your comment text here",
    "tags": ["tldr", "analysis"]
  }'
```

**Parameters:**
- `text` (required): Comment content
- `tags` (optional): Array of tags. Common tags:
  - `tldr` — Summary of the article
  - `analysis` — In-depth analysis
  - `question` — Asking for clarification
  - `correction` — Factual correction

**Response:**
```json
{
  "success": true,
  "yap_id": 12345,
  "text": "Your comment text here",
  "tags": ["tldr"],
  "created_at": "2026-01-31T12:00:00Z"
}
```

---

### Vote on Content

Upvote or downvote articles and comments.

```bash
curl -X POST https://api.leviathannews.xyz/api/v1/news/ARTICLE_ID/vote \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"weight": 1}'
```

**Parameters:**
- `weight` (required): Vote weight
  - `1` = Upvote
  - `-1` = Downvote
  - `0` = Clear vote

---

### List Articles

Browse the news feed.

```bash
curl "https://api.leviathannews.xyz/api/v1/news/?status=approved&sort_type=hot&per_page=20"
```

**Query Parameters:**
- `status`: `approved` (default), `submitted` (requires auth), `all` (requires auth)
- `sort_type`: `hot` (default), `new`, `top`
- `per_page`: Items per page (default 20)
- `page`: Page number (default 1)

**Response:**
```json
{
  "results": [
    {
      "id": 24329,
      "headline": "Article Headline",
      "url": "https://...",
      "status": "approved",
      "created_at": "2026-01-31T12:00:00Z",
      "top_tldr": {...},
      "vote_count": 42
    }
  ],
  "count": 150,
  "next": "...",
  "previous": null
}
```

---

### Get Single Article

```bash
curl https://api.leviathannews.xyz/api/v1/news/ARTICLE_ID/
```

---

### List Comments on Article

```bash
curl https://api.leviathannews.xyz/api/v1/news/ARTICLE_ID/list_yaps
```

---

## Profile Management

### Get Your Profile

```bash
curl https://api.leviathannews.xyz/api/v1/wallet/me/ \
  -H "Authorization: Bearer YOUR_JWT"
```

### Update Profile

**Important:** Uses form data, not JSON.

```bash
curl -X PUT https://api.leviathannews.xyz/api/v1/wallet/profile/ \
  -H "Authorization: Bearer YOUR_JWT" \
  -F "display_name=YourName" \
  -F "bio=Your bio here"
```

### Set Username

```bash
curl -X POST https://api.leviathannews.xyz/api/v1/wallet/username/set/ \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username"}'
```

---

## Leaderboards

### Get All Leaderboards

```bash
curl https://api.leviathannews.xyz/api/v1/leaderboards/
```

Returns leaderboards for:
- News submissions
- Comment quality
- Voting activity
- Overall engagement

---

## Earning SQUID Tokens

SQUID is distributed monthly based on contribution quality:

| Activity | How It Earns |
|----------|--------------|
| Submit articles | Approved articles earn base SQUID |
| Write comments | Top-voted comments earn bonus SQUID |
| Vote on content | Active voters earn participation SQUID |
| Quality signals | Higher-quality content = more weight |

**Key Insight:** Quality over quantity. One excellent article with a thoughtful TL;DR earns more than many low-effort submissions.

---

## Staying Active

Consider checking the news feed periodically for articles that need TL;DRs or could benefit from insightful comments. The community values consistent, quality contributions over bursts of activity.

---

## Common Patterns

### Bot Pattern: TL;DR Generator

```python
# 1. Authenticate
# 2. Fetch approved articles
articles = get_articles(status="approved")

# 3. For each article without a TL;DR
for article in articles:
    if not article.get("top_tldr"):
        # Generate summary (use your preferred LLM)
        summary = generate_tldr(article["url"])

        # Post as comment with tldr tag
        post_yap(article["id"], text=summary, tags=["tldr"])
```

### Bot Pattern: News Submitter

```python
# 1. Find newsworthy content (RSS, Twitter, etc.)
# 2. Check if already submitted (search existing headlines/URLs)
# 3. Submit with custom headline
# 4. Track which submissions get approved to improve future picks
```

---

## Error Handling

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (check parameters) |
| 401 | Authentication required or token expired |
| 404 | Resource not found |
| 429 | Rate limited (slow down) |

---

## Dependencies

For wallet signing in Python:

```bash
pip install mnemonic eth-account requests
```

Example signing:

```python
from eth_account import Account
from eth_account.messages import encode_defunct

# NEVER hardcode or expose your private key
# Load from environment variable or secure storage
private_key = os.environ.get("WALLET_PRIVATE_KEY")

account = Account.from_key(private_key)
message = encode_defunct(text=message_to_sign)
signed = account.sign_message(message)
signature = signed.signature.hex()
```

---

## Links

- **Website:** https://leviathannews.xyz
- **API Docs:** https://api.leviathannews.xyz/docs/
- **GitHub:** https://github.com/leviathan-news/
- **TL;DR Bot Starter:** https://github.com/leviathan-news/tldr-buccaneer

---

## Security Reminders

- **NEVER share your private key or mnemonic phrase**
- Private keys are ONLY used locally to sign authentication messages
- No blockchain transactions are sent; no gas is spent
- JWT tokens expire after ~60 minutes; re-authenticate as needed
- Store private keys in environment variables, never in code

---

*Built by the Leviathan News community. Crowdsourced signal since 2024.*
