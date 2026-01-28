# Core Patch Details

This document describes the exact changes made to core Clawdbot files.

## File 1: `dist/auto-reply/reply/dispatch-from-config.js`

### Location of Changes

Lines 101-111 (detection logic):
```javascript
const inboundAudio = isInboundAudioContext(ctx);
const sessionTtsAuto = resolveSessionTtsAuto(ctx, cfg);
// Disable block streaming when TTS should produce audio for this response.
// Block streaming drops final payloads (text already sent as blocks), but
// TTS only fires on "final" kind payloads (default mode), so TTS never
// triggers when block streaming is active.  Disabling block streaming for
// TTS-eligible messages ensures the final reply carries text for synthesis.
const ttsAutoResolved = normalizeTtsAutoMode(sessionTtsAuto) ?? normalizeTtsAutoMode(cfg.messages?.tts?.auto);
const ttsWillFire = ttsAutoResolved === "always" || (ttsAutoResolved === "inbound" && inboundAudio);
// DEBUG: TTS pipeline tracing
console.log(`[TTS-DEBUG] inboundAudio=${inboundAudio} sessionTtsAuto=${sessionTtsAuto} ttsAutoResolved=${ttsAutoResolved} ttsWillFire=${ttsWillFire} MediaType=${ctx.MediaType} MediaTypes=${JSON.stringify(ctx.MediaTypes)} Body=${(ctx.Body ?? "").slice(0, 80)}`);
```

Line 232 (application):
```javascript
disableBlockStreaming: ttsWillFire || params.replyOptions?.disableBlockStreaming,
```

Line 234 (skip onBlockReply when TTS will fire):
```javascript
// Don't provide onBlockReply when TTS will fire - we need the full final payload for synthesis
onBlockReply: ttsWillFire ? undefined : (payload, context) => {
```

### Key Additions

1. **`isInboundAudioContext(ctx)`** - Already existed, now used for TTS detection
2. **`resolveSessionTtsAuto(ctx, cfg)`** - Already existed, now used for TTS detection
3. **`ttsWillFire`** variable - NEW, determines if TTS should fire for this message
4. **Debug logging** - NEW, shows TTS detection logic
5. **`disableBlockStreaming: ttsWillFire`** - NEW, disables block streaming when TTS will fire

## File 2: `dist/tts/tts.js`

### Location of Changes

Line 813 (in `textToSpeech()`):
```javascript
console.log(`[TTS-SPEECH] entry: channel=${params.channel} channelId=${channelId} textLen=${params.text.length} maxLen=${config.maxTextLength}`);
```

Line 815:
```javascript
console.log(`[TTS-SPEECH] FAIL: text too long`);
```

Line 825:
```javascript
console.log(`[TTS-SPEECH] provider=${provider} userProvider=${userProvider} providers=${JSON.stringify(providers)} apiKey=${config.elevenlabs.apiKey ? "SET(" + config.elevenlabs.apiKey.slice(0, 8) + "...)" : "MISSING"}`);
```

Line 1054 (in `maybeApplyTtsToPayload()`):
```javascript
console.log(`[TTS-APPLY] entry: autoMode=${autoMode} kind=${params.kind} inboundAudio=${params.inboundAudio} channel=${params.channel} provider=${config.provider} apiKey=${config.elevenlabs.apiKey ? "SET" : "MISSING"}`);
```

Lines 1056, 1075, 1079, 1084, 1088, 1092, 1096, 1100, 1103 - Various `[TTS-APPLY] SKIP:` messages

Line 1103:
```javascript
console.log(`[TTS-APPLY] PASSED all checks, proceeding to textToSpeech. textLen=${ttsText.trim().length}`);
```

Line 1134:
```javascript
console.log(`[TTS-APPLY] calling textToSpeech with ${textForAudio.length} chars, channel=${params.channel}`);
```

Line 1142:
```javascript
console.log(`[TTS-APPLY] textToSpeech result: success=${result.success} audioPath=${result.audioPath ?? "none"} error=${result.error ?? "none"} provider=${result.provider ?? "none"} latency=${result.latencyMs ?? "?"}ms`);
```

Line 1154:
```javascript
console.log(`[TTS-APPLY] SUCCESS: audioPath=${result.audioPath} shouldVoice=${shouldVoice}`);
```

Line 1168:
```javascript
console.log(`[TTS-APPLY] FAILED: ${result.error ?? "unknown"}`);
```

### Key Additions

All additions are debug logging with prefixes:
- **`[TTS-SPEECH]`** - Shows TTS synthesis attempts and results
- **`[TTS-APPLY]`** - Shows TTS payload processing decisions

## Summary of Changes

### dispatch-from-config.js
- **Lines added**: ~15 lines
- **Lines modified**: 3 lines
- **Purpose**: Detect when TTS will fire and disable block streaming

### tts.js
- **Lines added**: ~15 lines
- **Lines modified**: 0 lines
- **Purpose**: Add debug logging to track TTS pipeline behavior

## Production Readiness

Before shipping to production:

1. **Remove or make configurable** all `console.log` statements:
   - Lines with `[TTS-DEBUG]`
   - Lines with `[TTS-APPLY]`
   - Lines with `[TTS-SPEECH]`

2. **Alternative**: Convert to proper debug logging:
   ```javascript
   if (logVerbose.enabled) {
     logVerbose(`[TTS-DEBUG] ...`);
   }
   ```

3. **Core logic to keep**:
   - The `ttsWillFire` detection (lines 101-109 in dispatch-from-config.js)
   - The `disableBlockStreaming: ttsWillFire` application (line 232)
   - The `onBlockReply: ttsWillFire ? undefined : ...` modification (line 234)

## Testing the Patch

To verify the patch works:

```bash
# 1. Apply the patch
cp patch/dispatch-from-config.js /path/to/clawdbot/dist/auto-reply/reply/
cp patch/tts.js /path/to/clawdbot/dist/tts/

# 2. Configure TTS
# In clawdbot.json:
{
  "messages": {
    "tts": {
      "auto": "inbound",
      "provider": "openai",
      "openai": { "apiKey": "sk-..." }
    }
  }
}

# 3. Send a voice memo to your bot

# 4. Check logs - you should see:
# [TTS-DEBUG] inboundAudio=true ttsAutoResolved=inbound ttsWillFire=true ...
# [TTS-APPLY] entry: autoMode=inbound kind=final inboundAudio=true ...
# [TTS-APPLY] PASSED all checks, proceeding to textToSpeech. textLen=...
# [TTS-SPEECH] entry: channel=telegram channelId=telegram textLen=...
# [TTS-APPLY] SUCCESS: audioPath=/tmp/tts-... shouldVoice=true
```

## Reverting the Patch

If you backed up the original files:
```bash
cp /path/to/clawdbot/dist/auto-reply/reply/dispatch-from-config.js.backup \
   /path/to/clawdbot/dist/auto-reply/reply/dispatch-from-config.js

cp /path/to/clawdbot/dist/tts/tts.js.backup \
   /path/to/clawdbot/dist/tts/tts.js
```

Or reinstall clawdbot:
```bash
npm install -g clawdbot@latest
```
