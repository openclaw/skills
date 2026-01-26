# ⚠️ DEPRECATED — Clawdbot Handles This Natively

**This skill is no longer needed.**

As of January 2026, Clawdbot has built-in OAuth support that:
- Connects to Claude via the setup wizard (`clawdbot onboard --auth-choice claude-cli`)
- Automatically refreshes tokens before expiry
- Updates auth profiles without any user intervention

**You don't need to install this skill.** Just run `clawdbot onboard` and select Claude CLI auth — it pulls tokens from Keychain automatically.

---

## What This Skill Was For

This skill was created to solve two issues before native support existed:
1. Getting Clawdbot to recognize Claude tokens from Keychain
2. Keeping tokens refreshed automatically

**Clawdbot now does both of these automatically.**

---

## If You Have This Installed

You can safely:
1. Remove the launchd job: `launchctl unload ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresh.plist`
2. Delete the skill folder: `rm -rf ~/clawd/skills/claude-connect`
3. Remove any related cron jobs

Your tokens will continue to work via Clawdbot's native support.

---

## Still Having Issues?

If `clawdbot onboard` doesn't find your Claude tokens:

1. Make sure Claude CLI is installed and logged in:
   ```bash
   claude
   # Then run: /login
   ```

2. Re-run the Clawdbot wizard:
   ```bash
   clawdbot onboard --auth-choice claude-cli
   ```

---

## Historical Reference

This repo is kept for historical reference only. The code is no longer maintained.

**Original purpose:** Connect Claude subscription to Clawdbot and keep tokens refreshed.

---

## License

MIT
