/**
 * Discord Voice Memo Upgrades
 *
 * This is a documentation-only package that contains patch files
 * for core Clawdbot modifications to enable TTS auto-replies for
 * voice memo messages.
 *
 * This file exists to satisfy Node.js package requirements but
 * does not export any functionality since this is a core patch,
 * not a plugin.
 */

module.exports = {
  name: 'discord-voice-memo-upgrades',
  version: '1.0.0',
  type: 'core-patch',
  description: 'Fixes voice memo TTS auto-replies by disabling block streaming when TTS will fire',

  // Metadata for documentation
  metadata: {
    filesModified: [
      'dist/auto-reply/reply/dispatch-from-config.js',
      'dist/tts/tts.js'
    ],
    keyChange: 'Added disableBlockStreaming: ttsWillFire to ensure final payload reaches TTS pipeline',
    debugLogging: 'Added [TTS-DEBUG], [TTS-APPLY], and [TTS-SPEECH] console logging',
    productionNote: 'Debug logging should be removed before production deployment'
  }
};
