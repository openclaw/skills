# 🚀 Deployment Guide

> Complete guide for deploying Smart Follow-ups to production

**Target**: Clawdbot with Telegram integration  
**User**: Robby (@robbyczgw-cla)  
**Status**: Ready for testing

---

## 📋 Pre-Deployment Checklist

### ✅ Completed
- [x] CLI tool implemented and tested
- [x] Handler integration completed
- [x] All documentation written
- [x] Package structure verified
- [x] Dependencies installed
- [x] License file included
- [x] .gitignore configured
- [x] Test scripts created

### 🔲 Before Production
- [ ] Set ANTHROPIC_API_KEY in production environment
- [ ] Test CLI with real API calls
- [ ] Test Telegram integration with live bot
- [ ] Set up error monitoring
- [ ] Configure rate limiting (if needed)
- [ ] Create GitHub repository
- [ ] Publish to npm (optional)
- [ ] Submit to ClawdHub

---

## 🛠️ Installation Steps

### 1. Environment Setup

```bash
# Set API key (REQUIRED)
export ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"

# Add to shell profile for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Verify Installation

```bash
cd /root/clawd/skills/smart-followups
./verify.sh
```

Expected output:
```
✅ All checks passed!
   The skill package is ready for testing.
```

### 3. Test CLI Standalone

```bash
./test.sh
```

This will:
- Test help command
- Generate follow-ups in all output modes
- Verify API connectivity
- Show sample outputs

### 4. Integrate with Clawdbot

**Option A: Symbolic Link** (Recommended for development)
```bash
ln -s /root/clawd/skills/smart-followups /path/to/clawdbot/skills/
```

**Option B: Copy** (For production)
```bash
cp -r /root/clawd/skills/smart-followups /path/to/clawdbot/skills/
```

### 5. Configure Clawdbot

Edit `clawdbot.config.json`:

```json
{
  "skills": {
    "smart-followups": {
      "enabled": true,
      "autoTrigger": false,
      "model": "claude-haiku-4"
    }
  }
}
```

**Settings**:
- `enabled`: Set to `true` to activate
- `autoTrigger`: Start with `false`, enable after testing
- `model`: Use `claude-haiku-4` for speed/cost

### 6. Restart Clawdbot

```bash
clawdbot daemon restart
```

Or if using systemd:
```bash
sudo systemctl restart clawdbot
```

---

## 🧪 Testing Protocol

### Phase 1: CLI Testing (5 minutes)

```bash
# Test 1: Basic functionality
echo '[{"user":"What is Docker?","assistant":"Docker is..."}]' | \
  node cli/followups-cli.js --mode json

# Test 2: Text mode
cat test-example.json | node cli/followups-cli.js --mode text

# Test 3: Telegram mode
cat test-example.json | node cli/followups-cli.js --mode telegram
```

**Success Criteria**:
- ✅ Returns valid JSON
- ✅ All 3 categories present (quick, deep, related)
- ✅ 2 questions per category
- ✅ No errors or warnings

### Phase 2: Clawdbot Integration (10 minutes)

**Test in Telegram**:

1. **Manual trigger test**:
   ```
   User: What is Rust?
   Bot: [Response about Rust]
   User: /followups
   ```
   
   **Expected**: 3 inline buttons appear (⚡🧠🔗)

2. **Button click test**:
   - Click any button
   - **Expected**: Question is sent automatically
   - **Expected**: Bot responds to that question

3. **Error handling test**:
   ```
   User: /followups
   ```
   (Without prior conversation)
   
   **Expected**: "Not enough conversation context" message

### Phase 3: Auto-Trigger Testing (Optional, 15 minutes)

**Enable auto-trigger**:
```json
{
  "skills": {
    "smart-followups": {
      "autoTrigger": true
    }
  }
}
```

**Restart Clawdbot**, then test:

1. **Auto-generation test**:
   ```
   User: What is Python?
   Bot: [Response about Python]
   ```
   
   **Expected**: Follow-up buttons appear automatically

2. **Multiple exchanges test**:
   - Have 3-4 back-and-forth exchanges
   - **Expected**: Suggestions evolve with conversation

3. **Disable and verify**:
   - Set `autoTrigger: false`
   - Restart Clawdbot
   - **Expected**: No auto-suggestions, manual `/followups` still works

---

## 📊 Monitoring & Metrics

### What to Monitor

1. **API Usage**:
   - Requests per day
   - Cost per day (~$0.0001 per request with Haiku)
   - Latency (target: <2s)

2. **User Engagement**:
   - `/followups` command usage
   - Button click-through rate
   - Most common suggestion types clicked

3. **Error Rate**:
   - API failures
   - Parse errors
   - Context extraction failures

### Logging Setup

Add to Clawdbot config:
```json
{
  "logging": {
    "skills": {
      "smart-followups": {
        "level": "info",
        "destination": "/var/log/clawdbot/smart-followups.log"
      }
    }
  }
}
```

**Log what**:
- Command invocations
- API errors
- Button clicks
- Generation latency

**Don't log**:
- Full conversation context (privacy)
- API keys
- User IDs (or hash them)

---

## 🔒 Security Hardening

### 1. API Key Protection

**Never**:
- ❌ Hardcode in source files
- ❌ Commit to git
- ❌ Expose in error messages
- ❌ Log in plain text

**Always**:
- ✅ Use environment variables
- ✅ Rotate keys periodically
- ✅ Use read-only access if possible

### 2. Rate Limiting

Add to `handler.js` (if high traffic expected):

```javascript
const rateLimit = new Map(); // userId -> lastRequest

function checkRateLimit(userId) {
  const now = Date.now();
  const lastRequest = rateLimit.get(userId);
  
  if (lastRequest && (now - lastRequest) < 10000) { // 10s cooldown
    throw new Error('Please wait before requesting more suggestions');
  }
  
  rateLimit.set(userId, now);
}
```

### 3. Input Validation

Already implemented in `parseContext()`:
- ✅ Validates exchange format
- ✅ Limits context to last 3 exchanges
- ✅ Handles malformed JSON gracefully

### 4. Error Handling

Already implemented:
- ✅ API errors caught and logged
- ✅ Parse errors handled
- ✅ User-friendly error messages

---

## 📈 Scaling Considerations

### Current Capacity
- **Users**: ~100 concurrent users
- **Requests**: ~1000/day comfortable
- **Cost**: ~$0.10/day @ 1000 requests

### If Scaling to 10,000+ Users

**1. Implement Caching**:
```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 min TTL

async function generateFollowups(exchanges) {
  const key = hashExchanges(exchanges);
  
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const result = await apiCall(exchanges);
  cache.set(key, result);
  return result;
}
```

**2. Queue System** (for auto-trigger mode):
```javascript
const queue = new Queue('followups');

queue.process(async (job) => {
  return await generateFollowups(job.data.exchanges);
});
```

**3. Load Balancing**:
- Multiple Clawdbot instances
- Shared Redis cache
- API request distribution

---

## 🐛 Troubleshooting

### Issue: "Module not found: @anthropic-ai/sdk"

**Solution**:
```bash
cd /root/clawd/skills/smart-followups
npm install
```

### Issue: Slow response times (>5s)

**Possible causes**:
1. Using Sonnet instead of Haiku
   - Check config: `"model": "claude-haiku-4"`
2. Network latency
   - Test: `ping api.anthropic.com`
3. Large context
   - Verify: Context limited to 3 exchanges

**Solution**: Review `SKILL.md` → Advanced Configuration

### Issue: Buttons not showing on Telegram

**Check**:
1. Channel detection: `console.log(channel)`
2. Clawdbot Telegram config
3. Bot permissions (inline keyboard permission)

**Debug**:
```javascript
// Add to handler.js
console.log('Channel:', context.channel);
console.log('Supports buttons:', supportsInlineButtons(context.channel));
```

### Issue: Repetitive suggestions

**Solution**: Increase temperature in `cli/followups-cli.js`:
```javascript
temperature: 0.8  // Up from 0.7
```

---

## 🔄 Rollback Plan

If issues arise in production:

### 1. Immediate Disable

Edit Clawdbot config:
```json
{
  "skills": {
    "smart-followups": {
      "enabled": false
    }
  }
}
```

Restart: `clawdbot daemon restart`

### 2. Revert to Previous Version

```bash
cd /root/clawd/skills/smart-followups
git checkout v0.9.0  # or previous tag
clawdbot daemon restart
```

### 3. Complete Removal

```bash
rm -rf /path/to/clawdbot/skills/smart-followups
clawdbot daemon restart
```

---

## 📦 Publishing to ClawdHub

### Prerequisites
- [ ] Tested thoroughly (all phases above)
- [ ] GitHub repository created (public)
- [ ] npm package published (optional)
- [ ] Screenshots/demo ready
- [ ] ClawdHub account created

### Submission Checklist

```yaml
name: smart-followups
version: 1.0.0
description: Generate contextual follow-up suggestions with inline buttons
author: Robby (@robbyczgw-cla)
repository: https://github.com/robbyczgw-cla/clawdbot-smart-followups
license: MIT
tags: [conversation, suggestions, ai, telegram, buttons]
channels: [telegram, discord, slack, signal, imessage]
tested_on: 
  - clawdbot: 1.0.0
  - telegram: true
  - signal: true
screenshots:
  - telegram_buttons.png
  - signal_text.png
demo_video: https://youtube.com/...
```

---

## 🎯 Success Metrics

After 1 week in production:

**Usage**:
- [ ] `/followups` used in >50% of conversations
- [ ] Button click-through rate >30%
- [ ] No critical errors

**Performance**:
- [ ] Average latency <2s
- [ ] API error rate <1%
- [ ] Cost within budget ($0.20/day)

**Feedback**:
- [ ] User satisfaction score >4/5
- [ ] No security incidents
- [ ] Feature requests collected

---

## 📞 Support & Maintenance

### Regular Maintenance (Weekly)
- Review logs for errors
- Check API usage and costs
- Monitor user feedback
- Update dependencies if needed

### Emergency Contacts
- **Clawdbot issues**: Clawdbot team
- **API issues**: Anthropic support
- **Skill issues**: @robbyczgw-cla

### Documentation Updates
- Keep CHANGELOG.md current
- Update examples with new use cases
- Add FAQs based on user questions

---

## ✅ Final Pre-Launch Checklist

- [ ] API key set and verified
- [ ] All tests passing
- [ ] Telegram integration tested
- [ ] Auto-trigger tested and disabled (start manual)
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Rollback plan documented
- [ ] Team briefed
- [ ] User documentation ready
- [ ] Launch date scheduled

---

**Deployment Status**: 🟡 Ready for Testing  
**Next Step**: Test with real Telegram bot  
**Target Launch**: After successful testing phase  
**Maintainer**: @robbyczgw-cla
