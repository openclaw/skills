# ClawdHub Publishing Guide

## Status
✅ GitHub repo created: https://github.com/brokemac79/webchat-audio-notifications  
⏳ ClawdHub publishing - ready to publish after login

---

## Prerequisites

✅ **ClawdHub CLI installed** (v0.3.0)
```bash
clawdhub --cli-version
# ClawdHub CLI v0.3.0
```

❌ **Not logged in yet**
```bash
clawdhub whoami
# Error: Not logged in
```

---

## Publishing Steps

### Step 1: Login to ClawdHub

You have two options:

**Option A: Browser login (Recommended)**
```bash
clawdhub login
```
This will:
- Open your browser
- Take you to clawdhub.com
- Generate an API token
- Store it locally

**Option B: Token login (Manual)**
```bash
clawdhub login --token YOUR_API_TOKEN --no-browser
```
You'd need to get a token from clawdhub.com first.

### Step 2: Verify Login
```bash
clawdhub whoami
```
Should show your username/account info.

### Step 3: Publish the Skill

From the project directory:
```bash
cd /home/ubuntu/clawd/webchat-audio-notifications

clawdhub publish . \
  --slug webchat-audio-notifications \
  --name "Webchat Audio Notifications" \
  --version 1.0.0 \
  --changelog "Initial release: POC with tab detection, volume control, and dual sound options"
```

**What this does:**
- Packages the entire directory
- Uploads to clawdhub.com
- Makes it searchable and installable
- Others can install with: `clawdhub install webchat-audio-notifications`

---

## Updating Published Skills

When you make changes and want to release a new version:

```bash
cd /home/ubuntu/clawd/webchat-audio-notifications

# Update version and changelog
clawdhub publish . \
  --slug webchat-audio-notifications \
  --name "Webchat Audio Notifications" \
  --version 1.0.1 \
  --changelog "Bug fixes: WebM fallback removed, sound switching improved"
```

---

## What Gets Published

Everything in the directory except:
- `.git/` (git internals)
- `node_modules/` (if any)
- Files in `.gitignore`

**What users get when they install:**
```
skills/webchat-audio-notifications/
├── client/
│   ├── howler.min.js
│   ├── notification.js
│   └── sounds/
├── examples/
│   └── test.html
├── docs/
│   └── integration.md
├── README.md
├── SKILL.md
└── LICENSE
```

---

## Installation (After Publishing)

Users can install with:
```bash
clawdhub install webchat-audio-notifications
```

Or search for it:
```bash
clawdhub search "audio notifications"
clawdhub search "webchat"
```

---

## Current Status Summary

| Step | Status | Command |
|------|--------|---------|
| CLI Installed | ✅ Done | `which clawdhub` |
| GitHub Repo | ✅ Done | https://github.com/brokemac79/webchat-audio-notifications |
| ClawdHub Login | ⏳ Needed | `clawdhub login` |
| Publish | ⏳ Ready | `clawdhub publish . --slug webchat-audio-notifications --name "Webchat Audio Notifications" --version 1.0.0 --changelog "Initial release"` |

---

## Next Actions

**Tonight (Optional):**
1. `clawdhub login` - Opens browser to authenticate

**Tomorrow (Recommended):**
1. Get community feedback first (Discord #showcase)
2. Iterate based on feedback if needed
3. Then publish to ClawdHub when ready

**Publishing Decision:**
- ✅ Publish now = Get it out there, iterate based on user feedback
- ✅ Wait for feedback = Polish based on Discord input first

Both are valid! POC is solid enough to publish now.

---

## Additional Commands

**Search existing skills:**
```bash
clawdhub search "notification"
clawdhub explore  # Browse latest
```

**List your published skills:**
```bash
clawdhub list
```

**Update after publishing:**
```bash
# Bump version in SKILL.md first, then:
clawdhub publish . --version 1.0.1 --changelog "Your changes"
```

---

## Troubleshooting

**"Not logged in" error:**
```bash
clawdhub login
```

**"Skill already exists" error:**
- Bump the version number
- Or delete and republish (not recommended)

**Want to unpublish:**
```bash
clawdhub delete webchat-audio-notifications
# Can undelete later with: clawdhub undelete
```

---

## Links

- **GitHub:** https://github.com/brokemac79/webchat-audio-notifications
- **ClawdHub:** https://clawdhub.com (after publishing)
- **Discord Thread:** https://discord.com/channels/1456350064065904867/1466181146374307881
- **Test Page:** http://localhost:8080/test.html (when server running)

---

**Ready to publish?** Just run:
```bash
clawdhub login
clawdhub publish /home/ubuntu/clawd/webchat-audio-notifications \
  --slug webchat-audio-notifications \
  --name "Webchat Audio Notifications" \
  --version 1.0.0 \
  --changelog "Initial POC release: Smart tab detection, volume control, dual sounds"
```
