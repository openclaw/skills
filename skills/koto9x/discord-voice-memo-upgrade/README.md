# Discord Voice Memo Upgrades for Moltbot/Clawdbot

Fixes voice memo TTS auto-replies by ensuring the final payload reaches the TTS synthesis pipeline when block streaming is enabled.

## Problem

When block streaming is enabled, intermediate text chunks are sent but the final assembled payload (which TTS hooks into) gets dropped. This prevents TTS from synthesizing audio responses for voice memo messages, even when TTS auto-reply is configured correctly.

## Solution

The fix disables block streaming temporarily when TTS will fire, ensuring the complete response payload reaches the TTS synthesis pipeline.

## Changes Made

### 1. `dispatch-from-config.js` (auto-reply/reply/)

**Core Fix**: Added logic to detect when TTS will fire and disable block streaming for that reply.

**Key Changes**:
- Added `disableBlockStreaming: ttsWillFire` — When TTS is going to fire (inbound audio message, TTS auto mode = "inbound", valid provider+apiKey), block streaming is disabled for that reply so the final payload reaches the TTS pipeline.
- Added detection logic for inbound audio context
- Added TTS pipeline configuration resolution
- Added debug logging (should be cleaned up for production)

**Detection Logic** (around line 101-111):
```javascript
const inboundAudio = isInboundAudioContext(ctx);
const sessionTtsAuto = resolveSessionTtsAuto(ctx, cfg);
const ttsAutoResolved = normalizeTtsAutoMode(sessionTtsAuto) ?? normalizeTtsAutoMode(cfg.messages?.tts?.auto);
const ttsWillFire = ttsAutoResolved === "always" || (ttsAutoResolved === "inbound" && inboundAudio);
```

**Applied at line 232**:
```javascript
disableBlockStreaming: ttsWillFire || params.replyOptions?.disableBlockStreaming,
```

### 2. `tts.js` (tts/)

**Debug Enhancements**: Added comprehensive logging to track TTS pipeline decisions.

**Changes**:
- Added `[TTS-DEBUG]` logging in `dispatchReplyFromConfig()` showing inboundAudio, ttsAutoResolved, ttsWillFire, MediaType, etc.
- Added `[TTS-APPLY]` debug logging at every early-return in `maybeApplyTtsToPayload()` — shows exactly which check causes TTS to skip
- Added `[TTS-SPEECH]` debug logging in `textToSpeech()` — shows the resolved provider chain and API key status

**Note**: Debug logging lines should be removed or converted to proper debug-level logging before production deployment.

## Files Modified

- `/path/to/clawdbot/dist/auto-reply/reply/dispatch-from-config.js`
- `/path/to/clawdbot/dist/tts/tts.js`

## What to Ship

The actual fix is just the `disableBlockStreaming: ttsWillFire` change in `dispatch-from-config.js`. The debug logging should be stripped before shipping to production.

## How It Works

1. When a voice memo arrives, `isInboundAudioContext()` detects the audio attachment
2. `resolveSessionTtsAuto()` checks the session's TTS auto mode setting
3. `ttsWillFire` is set to `true` if conditions are met (inbound audio + auto mode)
4. Block streaming is disabled for this reply only
5. The complete response payload reaches `maybeApplyTtsToPayload()`
6. TTS synthesis occurs and audio is returned

## Installation

Since these are core Clawdbot modifications, you'll need to either:

1. **Apply the patch** to your Clawdbot installation (see `patch/` directory)
2. **Wait for upstream merge** if this gets accepted into core Clawdbot
3. **Manually edit** the files in your `node_modules/clawdbot/dist/` directory

## Testing

To verify the fix works:

1. Configure TTS with `auto: "inbound"` mode
2. Send a voice memo to your bot via Discord/Telegram
3. Check logs for `[TTS-DEBUG]` and `[TTS-APPLY]` messages
4. Verify bot responds with synthesized audio

## Production Recommendations

Before deploying to production:
- Remove all `console.log` debug statements
- Consider making the logging configurable via debug levels
- Add tests for the TTS detection logic
- Document the configuration options

## Version

- **Version**: 1.0.0
- **Clawdbot Core Version**: Compatible with latest
- **Author**: k121
- **Date**: 2026-01-28

## License

Same as Moltbot.
