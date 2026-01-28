# Locus — Payment Tools for AI Agents

Locus connects your ClawdBot agent to a crypto wallet via MCP, enabling payments, balance checks, and token management.

## Quick Start

1. **Install the skill:**
   ```bash
   clawdhub install locus
   ```

2. **Run setup from your ClawdBot workspace root:**
   ```bash
   bash skills/locus/scripts/setup.sh
   ```

3. **Get your API key** at https://app.paywithlocus.com — each key is tied to your wallet and permission group.

4. **Verify it works:**
   ```bash
   mcporter list locus
   ```

That's it! Your agent can now send payments, check balances, and manage token approvals.

## Manual Setup (without script)

If you prefer to configure manually:
```bash
npm i -g mcporter    # if not installed
mcporter config add locus \
  --url "https://mcp.paywithlocus.com/mcp" \
  --header "Authorization=Bearer YOUR_API_KEY" \
  --scope home
```

## What Your Agent Can Do

Tools vary by permission group, but typically include:
- **get_payment_context** — Budget status & whitelisted contacts
- **list_tokens** — Available tokens with balances and limits
- **send_token** — Send to wallet address, ENS name, or email
- **send_token_multi** — Batch send multiple tokens
- **approve_token** — Set ERC-20 spending allowances

## Learn More

https://paywithlocus.com
