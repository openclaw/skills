# 🔔 Webchat Audio Notifications

Browser audio notifications for Moltbot/Clawdbot webchat. Get notified when new messages arrive - but only when the tab is in the background.

**🧪 [Try the live demo](examples/test.html)** - Download and open in your browser!

**Status:** ✅ v1.2.0 - Production ready, looking for testers!

---

## 🚀 Quick Test (2 minutes)

**Want to try it right now?**

1. **Clone or download** this repo
2. **Open** `examples/test.html` in your browser
3. **Click** the green "🔊 Test Sound" button (unlocks audio)
4. **Hear** the notification sound!
5. **Try** different intensity levels (Level 1-5 dropdown)

That's it! If you hear sounds, it works. 🎉

### ⚠️ Important: Browser Autoplay Policy

**Why you must click "Test Sound" first:**

All modern browsers (Chrome, Firefox, Safari, Edge) **block audio autoplay by default** as a security feature. This prevents websites from playing sounds without your permission.

**This is NORMAL and EXPECTED behavior, not a bug!**

**What happens:**
1. Page loads → Audio is blocked 🔇
2. You click "Test Sound" (or any button) → Audio unlocks 🔊
3. From now on, notifications work automatically ✅

**You only need to click once per session.** After that, all sounds play normally. This is how all web audio works - YouTube, Spotify, etc. all require a click first.

If you don't click first and don't hear sounds, that's why! Just click the Test Sound button.

---

## ✨ Features

- 🔔 **Smart notifications** - Only plays sound when tab is hidden
- 🎚️ **Volume control** - Adjustable notification volume (0-100%)
- 🔕 **Easy toggle** - Enable/disable with one click
- 🎵 **5 intensity levels** - From whisper (level 1) to impossible-to-miss (level 5)
- 📁 **Custom sounds** - Upload your own notification sounds (MP3, WAV, OGG, WebM)
- 💾 **Persistent preferences** - Settings saved in localStorage
- 📱 **Mobile-friendly** - Graceful handling of mobile restrictions
- 🚫 **Autoplay handling** - Respects browser autoplay policies
- ⏱️ **Cooldown** - Prevents notification spam (3s between alerts)
- 🐞 **Debug mode** - Optional logging for troubleshooting

## 🎯 Quick Start

### Three Easy Setup Options

**Want easy configuration?** → [Easy Setup Guide](docs/EASY_SETUP.md)

1. **Drop-in Settings Panel** - Ready-made UI (recommended)
2. **JSON Configuration** - Config file approach
3. **Programmatic** - Full control via code

### 1. Test the POC

Open `examples/test.html` or `examples/easy-setup.html` in your browser:

```bash
cd webchat-audio-notifications/examples
python3 -m http.server 8080
# Open http://localhost:8080/test.html
```

**Test steps:**
1. Click "Enable Notifications" if prompted
2. Switch to another tab
3. Click "Trigger Notification" (or have someone trigger it)
4. You should hear a sound! 🔊

### 2. Basic Integration

**Simplest (with settings UI):**
```html
<!-- Load libraries -->
<script src="./howler.min.js"></script>
<script src="./notification.js"></script>

<script>
  let notifier = null;
  window.addEventListener('DOMContentLoaded', async () => {
    notifier = new WebchatNotifications({
      soundPath: './sounds',
      soundName: 'level3'
    });
    await notifier.init();
  });
</script>

<!-- Add settings panel (users can configure themselves) -->
<div id="notification-settings"></div>
<script>
  fetch('./settings-panel.html')
    .then(r => r.text())
    .then(html => {
      document.getElementById('notification-settings').innerHTML = html;
    });
</script>
```

**Programmatic (full control):**
```html
<script src="./howler.min.js"></script>
<script src="./notification.js"></script>

<script>
  const notifier = new WebchatNotifications({
    soundPath: './sounds',
    soundName: 'level3',
    defaultVolume: 0.7
  });
  
  await notifier.init();
  
  // Trigger notification when new message arrives
  socket.on('message', (msg) => {
    notifier.notify();
  });
</script>
```

👉 **[Full Easy Setup Guide](docs/EASY_SETUP.md)** - Settings panel, JSON config, and more!

## 📚 API Documentation

### Constructor

```javascript
const notifier = new WebchatNotifications(options);
```

**Options:**
```javascript
{
  soundPath: './sounds',               // Path to sounds directory
  soundName: 'level3',                 // Intensity: 'level1' through 'level5'
  defaultVolume: 0.7,                  // Volume level (0.0 to 1.0)
  cooldownMs: 3000,                    // Min time between notifications (ms)
  enableButton: true,                  // Show enable prompt if autoplay blocked
  debug: false                         // Enable console logging
}
```

**Sound Intensity Levels:**
- `level1` - Whisper (9.5KB) - Most subtle
- `level2` - Soft (12KB) - Gentle chime
- `level3` - Medium (13KB) - **Default**, balanced
- `level4` - Loud (43KB) - Attention-getting
- `level5` - Very Loud (63KB) - Impossible to miss

### Methods

#### `init()`
Initialize the notification system. Must be called after Howler.js loads.

```javascript
await notifier.init();
```

#### `notify(eventType?)`
Trigger a notification (only plays if tab is hidden).

```javascript
notifier.notify();           // Default notification
notifier.notify('message');  // Message notification (future: different sounds)
```

#### `test()`
Play notification sound immediately (ignores tab state, useful for testing).

```javascript
notifier.test();
```

#### `setEnabled(enabled)`
Enable or disable notifications.

```javascript
notifier.setEnabled(true);   // Enable
notifier.setEnabled(false);  // Disable
```

#### `setVolume(volume)`
Set notification volume (0.0 to 1.0).

```javascript
notifier.setVolume(0.5);  // 50% volume
notifier.setVolume(1.0);  // 100% volume
```

#### `setSound(soundName)`
Change notification intensity level.

```javascript
notifier.setSound('level1');  // Whisper (most subtle)
notifier.setSound('level2');  // Soft
notifier.setSound('level3');  // Medium (default)
notifier.setSound('level4');  // Loud
notifier.setSound('level5');  // Very loud (impossible to miss)
notifier.setSound('custom');   // Use uploaded custom sound
```

#### `uploadCustomSound(file)`
Upload a custom notification sound.

```javascript
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

const success = await notifier.uploadCustomSound(file);
if (success) {
  notifier.setSound('custom');  // Switch to custom sound
}
```

**Supported formats:** MP3, WAV, OGG, WebM  
**Max file size:** 500KB  
**Storage:** Browser localStorage (no server upload)

#### `removeCustomSound()`
Remove the uploaded custom sound.

```javascript
notifier.removeCustomSound();
```

#### `getCustomSound()`
Get info about the uploaded custom sound.

```javascript
const custom = notifier.getCustomSound();
if (custom) {
  console.log('Custom sound:', custom.name);
}
// Returns: { name, dataUrl } or null
```

#### `getSettings()`
Get current settings.

```javascript
const settings = notifier.getSettings();
// Returns: { enabled, volume, soundName, isMobile, initialized }
```

## 🌐 Browser Compatibility

| Browser | Version | Support | Notes |
|---------|---------|---------|-------|
| Chrome | 92+ | ✅ Full | Strictest autoplay policy |
| Firefox | 90+ | ✅ Full | Slightly more permissive |
| Safari | 15+ | ✅ Full | Requires WebKit prefixes (handled) |
| Edge | 92+ | ✅ Full | Chromium-based |
| Mobile Chrome | Latest | ⚠️ Limited | Requires user gesture per play |
| Mobile Safari | Latest | ⚠️ Limited | iOS restrictions apply |

**Overall compatibility:** 92% of users (based on Web Audio API support)

## ⚙️ Configuration Examples

### Simple Setup

```javascript
const notifier = new WebchatNotifications({
  soundPath: './sounds',
  soundName: 'level3'  // Medium intensity (default)
});
await notifier.init();
notifier.notify();  // That's it!
```

### Advanced Setup

```javascript
const notifier = new WebchatNotifications({
  soundPath: '/assets/sounds',
  soundName: 'level3',  // Start with medium
  defaultVolume: 0.8,
  cooldownMs: 5000,     // 5 second cooldown
  debug: true           // Enable logging
});

await notifier.init();

// Hook into your message system
chatClient.on('newMessage', () => notifier.notify());
chatClient.on('mention', () => {
  notifier.setSound('level5');  // Use loudest for mentions
  notifier.notify();
});
```

### With User Controls

```html
<!-- Volume slider -->
<input type="range" min="0" max="100" value="70" 
       onchange="notifier.setVolume(this.value / 100)">

<!-- Sound intensity selector -->
<select onchange="notifier.setSound(this.value)">
  <option value="level1">🔕 Level 1 - Whisper</option>
  <option value="level2">🔔 Level 2 - Soft</option>
  <option value="level3" selected>🔔 Level 3 - Medium</option>
  <option value="level4">🔊 Level 4 - Loud</option>
  <option value="level5">📢 Level 5 - Very Loud</option>
</select>

<!-- Enable/disable toggle -->
<button onclick="notifier.setEnabled(true)">Enable 🔔</button>
<button onclick="notifier.setEnabled(false)">Disable 🔕</button>

<!-- Test button -->
<button onclick="notifier.test()">Test Sound 🔊</button>

<!-- Custom sound upload -->
<input type="file" id="custom-sound" accept="audio/*" onchange="uploadCustom(this)">
<script>
  async function uploadCustom(input) {
    const file = input.files[0];
    if (await notifier.uploadCustomSound(file)) {
      notifier.setSound('custom');
      alert('Custom sound uploaded!');
    }
  }
</script>
```

### Custom Sound Upload Example

Users can upload their own notification sounds:

```html
<input type="file" id="sound-upload" accept="audio/mpeg,audio/wav,audio/ogg,audio/webm">

<script>
  document.getElementById('sound-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Upload the sound
    const success = await notifier.uploadCustomSound(file);
    
    if (success) {
      // Automatically switch to custom sound
      notifier.setSound('custom');
      console.log('Custom sound uploaded:', file.name);
      
      // Test it
      notifier.test();
    } else {
      console.error('Upload failed - check file type and size');
    }
  });
  
  // Check if custom sound exists
  const customSound = notifier.getCustomSound();
  if (customSound) {
    console.log('Custom sound available:', customSound.name);
  }
</script>
```

**Limitations:**
- Max file size: 500KB
- Supported formats: MP3, WAV, OGG, WebM
- Stored in browser localStorage (no server upload)
- Clearing browser data removes custom sound

## 🚨 Troubleshooting

### No sound playing?

**1. Check browser autoplay policy:**
- Click anywhere on the page first (browser may require user interaction)
- Look for the enable notification prompt
- Check browser console for errors

**2. Verify tab is hidden:**
- Notifications only play when tab is in background
- Use `notifier.test()` to test regardless of tab state

**3. Check volume:**
```javascript
console.log(notifier.getSettings().volume);  // Should be > 0
notifier.setVolume(1.0);  // Try max volume
```

**4. Verify files are accessible:**
- Open browser console
- Check Network tab for 404 errors on sound files
- Ensure sound files are in the correct path

### Sound plays when tab is active?

This shouldn't happen - it's a bug! The `document.hidden` check should prevent this.

**Debug steps:**
1. Enable debug mode: `new WebchatNotifications({ debug: true })`
2. Check console for "Tab is visible, skipping notification" message
3. If not appearing, there may be a Page Visibility API issue

### Mobile not working?

iOS Safari and mobile browsers have strict audio restrictions:
- Requires user gesture for EACH audio play (not just once)
- Background tab audio may be blocked entirely
- Consider using visual notifications (flashing favicon) on mobile

**Detect mobile:**
```javascript
const settings = notifier.getSettings();
if (settings.isMobile) {
  console.log('Mobile detected - audio may be limited');
}
```

## 📦 File Structure

```
webchat-audio-notifications/
├── client/
│   ├── notification.js       # Main notification class (10KB)
│   ├── howler.min.js         # Howler.js library (36KB)
│   ├── settings-panel.html   # Drop-in settings UI (8KB)
│   ├── config-loader.js      # JSON config helper (2KB)
│   ├── config.example.json   # Example configuration
│   └── sounds/
│       ├── level1.mp3        # Level 1 - Whisper (9.5KB)
│       ├── level2.mp3        # Level 2 - Soft (12KB)
│       ├── level3.mp3        # Level 3 - Medium (13KB, default)
│       ├── level4.mp3        # Level 4 - Loud (43KB)
│       ├── level5.mp3        # Level 5 - Very Loud (63KB)
│       ├── notification.mp3  # Legacy (same as level3)
│       ├── alert.mp3         # Legacy (same as level5)
│       └── SOUNDS.md         # Sound attribution & guide
├── examples/
│   ├── test.html            # Full test page with all features
│   └── easy-setup.html      # Simple demo with settings panel
├── docs/
│   ├── EASY_SETUP.md        # Easy setup guide (settings panel, JSON, etc.)
│   └── integration.md       # Advanced integration guide
├── README.md                # This file
└── SKILL.md                 # ClawdHub metadata
```

## 🔐 Privacy & Security

- **No external requests** - All assets loaded locally
- **localStorage only** - Preferences stored in user's browser
- **No tracking** - Zero analytics or telemetry
- **No permissions required** - Works with standard Web Audio API

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Credits

- **Audio library:** [Howler.js](https://howlerjs.com/) by James Simpson (MIT License)
- **Sound files:** [Mixkit.co](https://mixkit.co/) (Royalty-free, commercial use allowed)
- **Created for:** [Moltbot/Clawdbot](https://github.com/moltbot/moltbot) community

## 🤝 Contributing

Found a bug? Have a feature request? 

1. Test with `examples/test.html` first
2. Enable debug mode to see console logs
3. Open an issue with browser version and console output

## 🚀 Next Steps

- [x] **Multiple intensity levels** (5 levels implemented)
- [ ] WebM sound format support (smaller files)
- [ ] Visual notification fallback (flashing favicon)
- [ ] System notifications API integration
- [ ] Settings UI component
- [ ] Do Not Disturb mode (time-based)
- [ ] Custom sound upload support

## 💡 Usage Tips

**Choosing Your Level:**
- **Open office?** Use level 1-2 (subtle, won't disturb neighbors)
- **Home office?** Use level 3 (balanced default)
- **Noisy environment?** Use level 4-5 (cuts through background noise)
- **Critical alerts only?** Use level 5 for important notifications

**Dynamic Switching:**
```javascript
// Soft for regular messages
notifier.setSound('level2');

// Loud for mentions
socket.on('mention', () => {
  notifier.setSound('level5');
  notifier.notify();
  setTimeout(() => notifier.setSound('level2'), 1000);
});
```

---

**Status:** ✅ POC v1.1.0 - 5 intensity levels  
**Last updated:** 2026-01-28  
**Maintained by:** @brokemac79
