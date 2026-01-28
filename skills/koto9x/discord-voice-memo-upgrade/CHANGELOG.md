# Changelog

All notable changes to the Discord Voice Memo Upgrades will be documented in this file.

## [1.0.0] - 2026-01-28

### Added
- Initial release of TTS voice memo auto-reply fix
- Core patch for `dispatch-from-config.js` to disable block streaming when TTS will fire
- Detection logic for inbound audio context
- Session-level TTS auto mode resolution
- Debug logging for TTS pipeline tracking in `tts.js`
- Comprehensive documentation of the fix

### Fixed
- Voice memo TTS auto-replies not working due to block streaming dropping final payloads
- TTS synthesis pipeline not receiving complete response payload
- Inbound audio messages not triggering TTS when auto mode = "inbound"

### Technical Details
- Added `ttsWillFire` detection based on inbound audio and TTS auto mode
- Added `disableBlockStreaming: ttsWillFire` to ensure final payload reaches TTS
- Added `[TTS-DEBUG]`, `[TTS-APPLY]`, and `[TTS-SPEECH]` debug logging

### Notes
- Debug logging should be removed or made configurable before production deployment
- This is a core modification, not a plugin - manual patching required
- Compatible with latest Moltbot versions
