# Upload Instructions for ClawdHub

This document explains how to upload the TTS Voice Memo Fix skill to ClawdHub.

## What You're Submitting

**Skill Name**: Discord Voice Memo Upgrades
**Version**: 1.0.0
**Type**: Core Patch / Documentation
**Category**: Core Enhancement

## Package Contents

- `README.md` - Overview and problem description
- `SKILL.md` - Detailed skill documentation
- `PATCH.md` - Technical patch details
- `CHANGELOG.md` - Version history
- `clawdbot.plugin.json` - Skill metadata
- `package.json` - npm package metadata
- `index.js` - Package entry point
- `patch/` - Directory containing modified core files
  - `dispatch-from-config.js` - Modified auto-reply dispatcher
  - `tts.js` - Modified TTS handler with debug logging

## Pre-Upload Checklist

- [x] README.md includes problem description and solution
- [x] SKILL.md includes installation and testing instructions
- [x] PATCH.md documents exact code changes
- [x] CHANGELOG.md lists all changes
- [x] clawdbot.plugin.json has correct metadata
- [x] package.json has correct version (1.0.0)
- [x] Patch files are included in `patch/` directory
- [x] Tarball created: `discord-voice-memo-upgrades-v1.0.0.tar.gz`

## Upload Methods

### Method 1: Upload Tarball

1. Navigate to https://clawdhub.com/upload
2. Select "Upload Skill Package"
3. Choose file: `discord-voice-memo-upgrades-v1.0.0.tar.gz`
4. Fill in metadata:
   - **Title**: Discord Voice Memo Upgrades
   - **Version**: 1.0.0
   - **Category**: Core Patch
   - **Description**: Fixes voice memo TTS auto-replies by disabling block streaming when TTS will fire
   - **Tags**: tts, voice, audio, voice-memo, text-to-speech, auto-reply, clawdbot, moltbot, core-patch
5. Submit

### Method 2: Upload Directory

If ClawdHub supports directory upload:

1. Navigate to https://clawdhub.com/upload
2. Select "Upload from Directory"
3. Choose directory: `/Users/k121/MEGA/DEV/local/clawd/skills/discord-voice-memo-upgrades/`
4. Fill in metadata (same as above)
5. Submit

### Method 3: Git Repository (Future)

If you create a GitHub repository for this skill:

```bash
cd /Users/k121/MEGA/DEV/local/clawd/skills/discord-voice-memo-upgrades
git init
git add .
git commit -m "Initial release: Discord Voice Memo Upgrades v1.0.0"
git remote add origin <your-repo-url>
git push -u origin main
```

Then submit the repository URL to ClawdHub.

## Metadata for Upload Form

Copy/paste these values when filling out the upload form:

**Name**: Discord Voice Memo Upgrades
**Slug**: discord-voice-memo-upgrades
**Version**: 1.0.0
**Author**: k121
**Category**: Core Patch
**Type**: Documentation

**Short Description**:
Fixes voice memo TTS auto-replies by disabling block streaming when TTS will fire

**Long Description**:
This skill provides a core patch for Moltbot that fixes voice memo TTS auto-replies. The issue occurs when block streaming prevents the final payload from reaching the TTS synthesis pipeline. The fix detects when TTS should fire and temporarily disables block streaming for that specific reply, ensuring the complete response reaches the TTS synthesis pipeline.

**Tags**:
tts, voice, audio, voice-memo, text-to-speech, auto-reply, clawdbot, moltbot, core-patch, bug-fix

**Requirements**:
- Clawdbot >= 1.0.0
- Node.js >= 18.0.0
- Manual patch application required

**Installation Type**: Manual Patch

**License**: MIT

## Notes for Reviewers

This is a **core patch**, not a traditional plugin. It modifies compiled dist files in the Clawdbot installation:

1. `dist/auto-reply/reply/dispatch-from-config.js`
2. `dist/tts/tts.js`

**Key Change**: Added `disableBlockStreaming: ttsWillFire` logic to ensure TTS receives final payloads.

**Debug Logging**: Includes extensive console.log debugging that should be removed for production.

## Post-Upload

After uploading, share the ClawdHub link:
- Discord: Share in #skills or #announcements
- Twitter/X: Tweet with #Clawdbot #Moltbot #TTS
- GitHub: Create issue/PR in clawdbot repo linking to ClawdHub skill

## Support

If users have questions or issues:
- Point them to the SKILL.md for installation instructions
- Point them to PATCH.md for technical details
- Encourage testing with different TTS providers

## Version History

- **1.0.0** (2026-01-28) - Initial release
