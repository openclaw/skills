# Discord Voice Memo Upgrades - Skill Documentation

## Overview

This skill provides a core patch for Moltbot that fixes voice memo TTS auto-replies. The issue occurs when block streaming prevents the final payload from reaching the TTS synthesis pipeline.

## Type

**Core Patch / Documentation**

This is not a traditional plugin that extends functionality - it's a documentation package with patch files for core Clawdbot modifications.

## Use Case

Use this if you're experiencing:
- Voice memos not triggering TTS responses
- TTS working for text messages but not audio messages
- TTS auto mode = "inbound" not functioning

## Installation Methods

### Method 1: Manual Patch (Recommended for Development)

```bash
# 1. Locate your clawdbot installation
CLAWDBOT_PATH=$(which clawdbot)
CLAWDBOT_DIR=$(dirname $(dirname $CLAWDBOT_PATH))

# 2. Backup original files
cp $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/auto-reply/reply/dispatch-from-config.js \
   $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/auto-reply/reply/dispatch-from-config.js.backup

cp $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/tts/tts.js \
   $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/tts/tts.js.backup

# 3. Apply patch
cp patch/dispatch-from-config.js $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/auto-reply/reply/
cp patch/tts.js $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/tts/

# 4. Restart clawdbot
clawdbot restart
```

### Method 2: Wait for Upstream

If this patch gets accepted into core Clawdbot, you can simply update:
```bash
npm install -g clawdbot@latest
```

## Configuration

No additional configuration needed beyond existing TTS settings. Ensure you have:

```json
{
  "messages": {
    "tts": {
      "auto": "inbound",  // or "always"
      "provider": "openai",  // or "elevenlabs" or "edge"
      "elevenlabs": {
        "apiKey": "your-key-here"
      }
    }
  }
}
```

## How to Test

1. Configure TTS with `auto: "inbound"`
2. Send a voice memo to your bot
3. Check logs for debug output:
   ```
   [TTS-DEBUG] inboundAudio=true ttsAutoResolved=inbound ttsWillFire=true
   [TTS-APPLY] PASSED all checks, proceeding to textToSpeech
   [TTS-SPEECH] ...
   ```
4. Verify bot responds with audio

## Debug Logging

The patch includes extensive debug logging. To view:
```bash
# Logs will show in your clawdbot console
clawdbot gateway start
```

Look for:
- `[TTS-DEBUG]` - Shows TTS detection logic
- `[TTS-APPLY]` - Shows TTS payload processing decisions
- `[TTS-SPEECH]` - Shows TTS synthesis attempt

## Production Deployment

**Important**: Before deploying to production, consider:

1. **Remove debug logging** - The `console.log` statements should be removed or made configurable
2. **Test thoroughly** - Ensure voice memos work correctly
3. **Monitor performance** - Disabling block streaming may impact streaming behavior

To remove debug logging, edit the patched files and remove lines containing:
- `console.log('[TTS-DEBUG]'`
- `console.log('[TTS-APPLY]'`
- `console.log('[TTS-SPEECH]'`

## Reverting

If you need to revert the patch:
```bash
# Restore backups
CLAWDBOT_PATH=$(which clawdbot)
CLAWDBOT_DIR=$(dirname $(dirname $CLAWDBOT_PATH))

cp $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/auto-reply/reply/dispatch-from-config.js.backup \
   $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/auto-reply/reply/dispatch-from-config.js

cp $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/tts/tts.js.backup \
   $CLAWDBOT_DIR/lib/node_modules/clawdbot/dist/tts/tts.js

clawdbot restart
```

## Technical Details

### The Problem

Block streaming is used to send incremental text chunks to the user as they're generated. However, TTS synthesis hooks into the "final" payload type by default. When block streaming is enabled:

1. Text chunks are sent as "block" payloads
2. The final assembled text is sent as a "final" payload
3. But block streaming optimization drops the final payload (text already sent)
4. TTS never fires because it only processes "final" payloads

### The Solution

The patch adds detection logic to identify when TTS should fire:
- Inbound message has audio attachment (`isInboundAudioContext()`)
- TTS auto mode is "inbound" or "always"
- Valid TTS provider and API key configured

When these conditions are met, block streaming is temporarily disabled for that specific reply, ensuring the final payload reaches the TTS pipeline.

### Code Flow

```
dispatchReplyFromConfig()
  ├─ isInboundAudioContext(ctx) → detects audio
  ├─ resolveSessionTtsAuto(ctx, cfg) → gets TTS settings
  ├─ ttsWillFire = conditions met?
  └─ getReplyFromConfig({ disableBlockStreaming: ttsWillFire })
       └─ maybeApplyTtsToPayload() receives final payload
            └─ textToSpeech() synthesizes audio
```

## Compatibility

- **Clawdbot**: 1.0.0+
- **Node.js**: 18+
- **Platforms**: All platforms supported by Clawdbot

## Known Issues

- Debug logging is verbose (should be removed for production)
- Modifies compiled dist files (not source)
- May need to reapply after clawdbot updates

## Contributing

To improve this patch:
1. Test with different TTS providers (OpenAI, ElevenLabs, Edge)
2. Test with different auto modes ("always", "inbound", "tagged")
3. Suggest optimizations to reduce debug logging overhead
4. Propose integration into core Clawdbot source

## Support

If you encounter issues:
1. Check logs for `[TTS-DEBUG]` output
2. Verify TTS configuration is correct
3. Ensure API keys are valid
4. Check that block streaming was actually disabled (`disableBlockStreaming: true` in logs)

## License

Same as Moltbot.
