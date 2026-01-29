---
name: webchat-audio-notifications
description: Add browser audio notifications to Moltbot/Clawdbot webchat with 5 intensity levels - from whisper to impossible-to-miss (only when tab is backgrounded).
version: 1.1.0
author: brokemac79
repository: https://github.com/brokemac79/webchat-audio-notifications
homepage: https://github.com/brokemac79/webchat-audio-notifications
tags:
  - webchat
  - notifications
  - audio
  - ux
  - browser
  - howler
metadata:
  clawdbot:
    emoji: 🔔
    compatibility:
      minVersion: "2026.1.0"
      browsers:
        - Chrome 92+
        - Firefox 90+
        - Safari 15+
        - Edge 92+
    dependencies:
      - howler.js (included)
    files:
      - client/howler.min.js
      - client/notification.js
      - client/sounds/notification.mp3
      - client/sounds/alert.mp3
    install:
      - kind: manual
        label: Install webchat audio notifications
        instructions: |
          1. Copy files to your webchat directory:
             - client/howler.min.js → /webchat/js/
             - client/notification.js → /webchat/js/
             - client/sounds/ → /webchat/sounds/
          
          2. Add to your webchat HTML before closing </body>:
          
          ```html
          <script src="/js/howler.min.js"></script>
          <script src="/js/notification.js"></script>
          <script>
            const notifier = new WebchatNotifications({
              soundPath: '/sounds/notification'
            });
            notifier.init();
          </script>
          ```
          
          3. Hook into message events:
          
          ```javascript
          socket.on('message', () => {
            if (notifier) notifier.notify();
          });
          ```
          
          4. Test by switching tabs and triggering a message
          
          See docs/integration.md for full guide.
---

# 🔔 Webchat Audio Notifications

Browser audio notifications for Moltbot/Clawdbot webchat. Plays a notification sound when new messages arrive - but only when the tab is in the background.

## Features

- 🔔 **Smart notifications** - Only plays when tab is hidden
- 🎚️ **Volume control** - Adjustable 0-100%
- 🎵 **5 intensity levels** - Whisper (1) to impossible-to-miss (5)
- 📁 **Custom sounds** - Upload your own (MP3, WAV, OGG, WebM)
- 🔕 **Easy toggle** - Enable/disable with one click
- 💾 **Persistent settings** - Preferences saved in localStorage
- 📱 **Mobile-friendly** - Graceful degradation on mobile
- 🚫 **Autoplay handling** - Respects browser policies
- ⏱️ **Cooldown** - Prevents spam (3s between alerts)
- 🐞 **Debug mode** - Optional logging

## Quick Start

### Test the POC

```bash
cd examples
python3 -m http.server 8080
# Open http://localhost:8080/test.html
```

**Test steps:**
1. Switch to another tab
2. Click "Trigger Notification"
3. Hear the sound! 🔊

### Basic Integration

```javascript
// Initialize
const notifier = new WebchatNotifications({
  soundPath: './sounds',
  soundName: 'level3',  // Medium intensity (default)
  defaultVolume: 0.7
});

await notifier.init();

// Trigger on new message
socket.on('message', () => notifier.notify());

// Use different levels for different events
socket.on('mention', () => {
  notifier.setSound('level5');  // Loudest for mentions
  notifier.notify();
});
```

## API

### Constructor Options

```javascript
new WebchatNotifications({
  soundPath: './sounds',               // Path to sounds directory
  soundName: 'level3',                 // level1 (whisper) to level5 (very loud)
  defaultVolume: 0.7,                  // 0.0 to 1.0
  cooldownMs: 3000,                    // Min time between alerts
  enableButton: true,                  // Show enable prompt
  debug: false                         // Console logging
});
```

**Intensity Levels:**
- `level1` - Whisper (9.5KB) - Most subtle
- `level2` - Soft (12KB) - Gentle
- `level3` - Medium (13KB) - Default
- `level4` - Loud (43KB) - Attention-getting
- `level5` - Very Loud (63KB) - Impossible to miss

### Methods

- `init()` - Initialize (call after Howler loads)
- `notify(eventType?)` - Trigger notification (only if tab hidden)
- `test()` - Play sound immediately (ignore tab state)
- `setEnabled(bool)` - Enable/disable notifications
- `setVolume(0-1)` - Set volume
- `setSound(level)` - Change intensity ('level1' through 'level5')
- `getSettings()` - Get current settings

## Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 92+ | ✅ Full |
| Firefox | 90+ | ✅ Full |
| Safari | 15+ | ✅ Full |
| Mobile | Latest | ⚠️ Limited |

**Overall:** 92% of users (Web Audio API support)

## File Structure

```
webchat-audio-notifications/
├── client/
│   ├── notification.js       # Main class (10KB)
│   ├── howler.min.js         # Audio library (36KB)
│   └── sounds/
│       ├── level1.mp3        # Whisper (9.5KB)
│       ├── level2.mp3        # Soft (12KB)
│       ├── level3.mp3        # Medium (13KB, default)
│       ├── level4.mp3        # Loud (43KB)
│       └── level5.mp3        # Very Loud (63KB)
├── examples/
│   └── test.html            # Standalone test with all levels
├── docs/
│   └── integration.md       # Integration guide
└── README.md                # Full documentation
```

## Integration Guide

See `docs/integration.md` for:
- Step-by-step setup
- Moltbot-specific hooks
- React/Vue examples
- Common patterns (@mentions, DND, badges)
- Testing checklist

## Configuration Examples

### Simple

```javascript
const notifier = new WebchatNotifications();
await notifier.init();
notifier.notify();
```

### Advanced

```javascript
const notifier = new WebchatNotifications({
  soundPath: '/assets/sounds',
  soundName: 'level2',  // Start with soft
  defaultVolume: 0.8,
  cooldownMs: 5000,
  debug: true
});

await notifier.init();

// Regular messages = soft
socket.on('message', () => {
  notifier.setSound('level2');
  notifier.notify();
});

// Mentions = very loud
socket.on('mention', () => {
  notifier.setSound('level5');
  notifier.notify();
});

// DMs = loud
socket.on('dm', () => {
  notifier.setSound('level4');
  notifier.notify();
});
```

### With UI Controls

```html
<input type="range" min="0" max="100" 
       onchange="notifier.setVolume(this.value / 100)">
<button onclick="notifier.test()">Test 🔊</button>
```

## Troubleshooting

**No sound?**
- Click page first (autoplay restriction)
- Check tab is actually hidden
- Verify volume > 0
- Check console for errors

**Sound plays when tab active?**
- Enable debug mode
- Check for "Tab is visible, skipping" message
- Report as bug if missing

**Mobile not working?**
- iOS requires user gesture per play
- Consider visual fallback (flashing favicon)

## Performance

- **Bundle:** ~122KB total (minified)
- **Memory:** ~2MB during playback
- **CPU:** Negligible (browser-native)
- **Network:** One-time download, cached

## Security

- ✅ No external requests
- ✅ localStorage only
- ✅ No tracking
- ✅ No special permissions

## License

MIT License

## Credits

- **Audio library:** [Howler.js](https://howlerjs.com/) (MIT)
- **Sounds:** [Mixkit.co](https://mixkit.co/) (Royalty-free)
- **Author:** @brokemac79
- **For:** [Moltbot/Clawdbot](https://github.com/moltbot/moltbot) community

## Contributing

1. Test with `examples/test.html`
2. Enable debug mode
3. Report issues with browser + console output

## Roadmap

- [ ] WebM format (smaller files)
- [ ] Per-event sounds (mention, DM, etc.)
- [ ] Visual fallback (favicon flash)
- [ ] System notifications API
- [ ] Settings UI component
- [ ] Do Not Disturb mode

---

**Status:** ✅ v1.1.0 Complete - 5 Intensity Levels  
**Tested:** Chrome, Firefox, Safari  
**Ready for:** Production use & ClawdHub publishing

## Links

- 📖 [README](./README.md) - Full documentation
- 🔧 [Integration Guide](./docs/integration.md) - Setup instructions
- 🧪 [Test Page](./examples/test.html) - Try it yourself
- 💬 [Discord Thread](https://discord.com/channels/1456350064065904867/1466181146374307881) - Community discussion
