# Crisp Skill for Clawdbot

This skill allows your AI agent to interact with Crisp customer support directly (read inbox, reply to customers, search history).

## Setup

### 1. Copy the folder
Place the `crisp` folder into your Clawdbot skills directory (e.g., `~/clawd/skills/crisp`).

### 2. Get Your Crisp Credentials

You need to create a **Crisp Plugin Token** to authenticate with the API.

**Steps:**
1. Go to [Crisp Marketplace](https://marketplace.crisp.chat/)
2. Click **"Create a Private Plugin"**
3. Choose a name for your plugin (e.g., "My Clawdbot Integration")
4. Request a **Development Token** (instant) or **Production Token** (requires approval)
5. Required scopes when creating the token:
   - ✅ `website:conversation:sessions` (Read)
   - ✅ `website:conversation:messages` (Read/Write)
   - ✅ `website:conversation:actions` (Read/Write)
6. Copy your **Token Identifier** and **Token Key**
7. Get your **Website ID** from the Crisp dashboard URL (e.g., `https://app.crisp.chat/website/YOUR_WEBSITE_ID/...`)

### 3. Configure Environment Variables

Add these to your shell profile (`.zshrc` or `.bashrc`) or export them before running Clawdbot:

```bash
export CRISP_WEBSITE_ID='YOUR_WEBSITE_ID'
export CRISP_TOKEN_ID='YOUR_TOKEN_IDENTIFIER'
export CRISP_TOKEN_KEY='YOUR_TOKEN_KEY'
```

**Example:**
```bash
export CRISP_WEBSITE_ID='abc12345-1234-5678-90ab-cdef12345678'
export CRISP_TOKEN_ID='e47d4438-f169-4487-86fc-fe2406a382b3'
export CRISP_TOKEN_KEY='a7d7103c3352683d0cdf7bf17f782facb6e41583a8906da1e05aaf9b91fcc40e'
```

### 4. Install Dependencies

The script uses Python 3 and the `requests` library.

```bash
pip3 install requests
```

## Usage

Once set up, you can ask your agent:
- "Check my Crisp inbox"
- "Draft a reply to the customer about X"
- "What was the last conversation with [email]?"
- "Show me unresolved conversations"
- "Send a message to session_xyz saying 'Thanks for reaching out!'"

## Troubleshooting

**❌ "CRISP_WEBSITE_ID, CRISP_TOKEN_ID, and CRISP_TOKEN_KEY environment variables required"**
- Make sure you've exported the environment variables in your current shell session
- Run `echo $CRISP_WEBSITE_ID` to verify it's set

**❌ "Error: invalid_data"**
- Check that your Website ID is correct
- Verify your token has the required scopes

**❌ "Error: unauthorized" or "Error: forbidden"**
- Your token may have expired or been revoked
- Regenerate a new token in the Crisp Marketplace

## Manual Testing

You can test the CLI directly:

```bash
# List inbox
python3 /path/to/skills/crisp/scripts/crisp.py inbox list --page 1 --max 5

# Search conversations
python3 /path/to/skills/crisp/scripts/crisp.py conversations search "email@example.com" --max 3

# Get messages from a conversation
python3 /path/to/skills/crisp/scripts/crisp.py messages get session_abc123 --max 10
```
