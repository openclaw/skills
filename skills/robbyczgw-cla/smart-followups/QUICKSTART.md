# 🚀 Quick Start Guide

Get Smart Follow-ups running in under 5 minutes.

## 1️⃣ Prerequisites

- Node.js 18+ installed
- Anthropic API key ([get one here](https://console.anthropic.com/))

## 2️⃣ Installation

```bash
cd /root/clawd/skills/smart-followups
npm install
chmod +x cli/followups-cli.js test.sh
```

## 3️⃣ Set API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Or add to `~/.bashrc` / `~/.zshrc` for persistence:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 4️⃣ Test It!

### Quick Test
```bash
./test.sh
```

This runs all output modes with sample data.

### Manual Test

```bash
# JSON output
cat test-example.json | node cli/followups-cli.js --mode json

# Text output (Signal/iMessage format)
cat test-example.json | node cli/followups-cli.js --mode text

# Telegram button format
cat test-example.json | node cli/followups-cli.js --mode telegram
```

### Custom Test

```bash
# Create your own conversation
echo '[{"user":"What is Rust?","assistant":"Rust is a systems programming language..."}]' | \
  node cli/followups-cli.js --mode text
```

## 5️⃣ Expected Output

**Text mode** should look like:

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. What are containers vs VMs?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. What about Kubernetes?

Reply with a number (1-3) to ask that question.
```

**JSON mode** should return:

```json
{
  "quick": "What are containers vs VMs?",
  "deep": "Explain Docker's architecture",
  "related": "What about Kubernetes?"
}
```

## 6️⃣ Integrate with Clawdbot

See [SKILL.md](./SKILL.md) for full integration guide.

**TL;DR**:

1. Copy this folder to Clawdbot's skills directory
2. Add to `clawdbot.config.json`:
   ```json
   {
     "skills": {
       "smart-followups": {
         "enabled": true,
         "autoTrigger": false
       }
     }
   }
   ```
3. Restart Clawdbot
4. Use `/followups` in any conversation

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY environment variable is required"

**Fix**: Set the API key (see step 3)

### "Error: Cannot find module '@anthropic-ai/sdk'"

**Fix**: Run `npm install` in this directory

### Very slow responses (>5 seconds)

**Check**: 
- Are you using Haiku? (`--model claude-haiku-4`)
- Network connection stable?
- Large conversation context?

### Errors about JSON parsing

**Likely**: API returned non-JSON. Check:
```bash
# Enable verbose logging (future feature)
DEBUG=* node cli/followups-cli.js ...
```

## 📚 Next Steps

- Read [README.md](./README.md) for feature overview
- Check [examples.md](./examples.md) for channel-specific outputs
- Review [SKILL.md](./SKILL.md) for Clawdbot integration
- Explore [INTERNAL.md](./INTERNAL.md) for architecture details

## 💡 Tips

1. **Use Haiku**: Default model, fastest and cheapest
2. **Manual trigger**: Start with `/followups` command, not auto-mode
3. **Test locally**: Verify CLI works before integrating with Clawdbot
4. **Monitor costs**: ~$0.0001 per generation with Haiku

## ✅ Checklist

- [ ] Node.js 18+ installed
- [ ] API key set as environment variable
- [ ] `npm install` completed
- [ ] `./test.sh` runs successfully
- [ ] CLI produces valid JSON/text output
- [ ] Ready to integrate with Clawdbot!

---

**Need help?** Check the main [README.md](./README.md) or open an issue.
