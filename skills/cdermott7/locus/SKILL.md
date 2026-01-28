---
name: locus
description: Locus payment tools for AI agents. Use when asked to send payments, check wallet balances, list tokens, approve token spending, or process payment-related actions from emails. Also use for demos of Locus (YC F25) payment infrastructure — scanning emails for payment requests and initiating crypto payments via wallet.
---

# Locus Payment Skill

Locus connects AI agents to crypto wallets via MCP. Tools are **dynamic** — each user gets different tools based on their permission group.

## Setup (Agent-Guided)

When the user asks to set up Locus, use payments, or anything payment-related — check if Locus is configured and walk them through setup interactively:

### Step 1: Check if mcporter is installed
```bash
command -v mcporter || npm i -g mcporter
```

### Step 2: Check if Locus is already configured
```bash
mcporter config get locus 2>/dev/null
```
If configured, skip to **Usage**. If the user wants to reconfigure, run:
```bash
mcporter config remove locus
```

### Step 3: Ask the user for their API key
Tell them:
> You'll need a Locus API key to connect your wallet. Get one at **https://app.paywithlocus.com** — each key is tied to your wallet and permission group. Paste it here when you're ready.

Wait for the user to provide their key. It should start with `locus_`. If it doesn't, warn them and confirm before proceeding.

### Step 4: Configure mcporter
```bash
mcporter config add locus \
  --url "https://mcp.paywithlocus.com/mcp" \
  --header "Authorization=Bearer <API_KEY>" \
  --scope home
```

### Step 5: Verify the connection
```bash
mcporter list locus
```
If tools appear, setup is complete — tell the user they're ready. If it fails, ask them to double-check their API key and try again.

### Alternative: Script-based setup
Users can also run the setup script directly from the Clawdbot workspace root:
```bash
bash skills/locus/scripts/setup.sh
```

## Usage

**Always discover available tools first:**
```bash
mcporter list locus --schema
```

This returns all tools the user's permission group allows. Tools vary per user — do not assume which tools exist. Use the schema output to understand parameters.

**Call any discovered tool:**
```bash
mcporter call locus.<tool_name> param1=value1 param2=value2
```

For array/object parameters:
```bash
mcporter call locus.<tool_name> --args '{"key": "value"}'
```

## Email → Payment Flow

1. Scan inbox for payment-related emails (invoices, bills, splits, reimbursements)
2. Identify actionable items with amounts, recipients, and context
3. Summarize findings to user
4. On user approval, execute payments via available tools
5. **Always confirm with user before sending any payment**

## Safety Rules

- **Never send payments without explicit user confirmation**
- Always show: recipient, token, amount, and memo before executing
- Check available balance before attempting payments
- Double-check recipient addresses — typos mean lost funds
- Confirm large payments (>$100) with extra care
