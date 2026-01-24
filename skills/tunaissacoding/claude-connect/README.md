# claude-connect

Connect Claude to Clawdbot instantly and keep it connected 24/7.

**The problem:** Clawdbot can't find your Claude Code token after setup, and tokens expire every 8 hours causing authentication failures.

**This tool:** Connects your Claude subscription to Clawdbot, then automatically refreshes tokens before they expire so you never see auth errors.

---

## ⚡ What It Does

**Your Claude subscription works with Clawdbot, and stays working.**

The tool:
- Connects your Claude tokens to Clawdbot's auth config
- Auto-refreshes tokens 30 minutes before they expire
- Runs silently in the background every few hours
- Handles duplicate/incomplete Keychain entries automatically

Zero manual intervention after initial setup.

---

## 🛠️ Getting Ready

Before installing this skill:

**You'll need:**
- **macOS 10.15 (Catalina) or later** with Keychain access
- **Active Claude subscription** (Pro, Max, Team, or Enterprise)

**Install through Homebrew:**

```bash
# Install jq (for JSON parsing)
brew install jq
```

**Set up Claude Code CLI:**

### Step 1: Install Claude Code CLI

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### Step 2: Log Into Your Claude Account

**Start Claude Code CLI:**
```bash
claude
```

**Then inside the CLI, run:**
```
/login
```

Follow the login prompts in your browser. **This creates the Keychain item** that stores your tokens.

---

## 🚀 Installation

**Run this right after installing Clawdbot** (after completing prerequisites above).

```bash
# Install the skill
clawdhub install claude-connect

# Connect Claude to Clawdbot
cd ~/clawd/skills/claude-connect
./refresh-token.sh
```

**Expected output:**
```
✅ Token still valid (475 minutes remaining)
Use --force to refresh anyway
```

**Done!** Claude is now connected to Clawdbot, and the connection stays alive 24/7.

---

### What This Does

**Solves two specific issues:**

1. **Connection:** Links your Claude subscription to Clawdbot
   - Reads from Keychain (where `claude` + `/login` stored tokens)
   - Writes to Clawdbot's auth-profiles.json
   - Clawdbot can now use Claude

2. **Maintenance:** Keeps the connection alive
   - Checks expiry every few hours
   - Refreshes 30 min before expiry
   - You never see auth failures

---

## 🔧 How It Works

**Result:** Claude stays connected without you thinking about it.

**The process:**

1. **Scans Keychain:** Finds all `"Claude Code-credentials"` entries
2. **Validates tokens:** Uses first entry with complete OAuth data
3. **Checks expiry:** Refreshes 30 minutes before token expires
4. **Calls OAuth API:** Gets new tokens from Anthropic
5. **Updates configs:** Writes to both Keychain and Clawdbot's auth-profiles.json

**Example (force refresh):**

```bash
./refresh-token.sh --force
```

Output:
```
Scanning for all 'Claude Code-credentials' entries...
Found 2 entry/entries
Checking entry with account: Claude Code
  ⚠ Entry incomplete, continuing...
Checking entry with account: claude
✓ Found complete OAuth tokens

Force refresh requested (token expires in 21 minutes)
Calling OAuth endpoint...
✓ Received new tokens
New expiry: 2026-01-24 09:27:17 (8 hours)
✓ Auth file updated
✓ Keychain updated

✅ Token refreshed successfully!
```
