# Easy Setup Guide

Three ways to set up notifications - choose what works best for you!

---

## 🚀 Option 1: Drop-in Settings Panel (Recommended)

**Best for:** Users who want a ready-made UI

Copy the files and include the settings panel:

```html
<!-- Load libraries -->
<script src="./howler.min.js"></script>
<script src="./notification.js"></script>

<!-- Initialize -->
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

<!-- Load settings panel (self-contained, no extra CSS needed) -->
<script>
  fetch('./settings-panel.html')
    .then(r => r.text())
    .then(html => {
      document.getElementById('notification-settings').innerHTML = html;
    });
</script>

<!-- Put the panel wherever you want it -->
<div id="notification-settings"></div>
```

**What you get:**
- ✅ Enable/disable toggle
- ✅ 5 intensity levels dropdown
- ✅ Volume slider
- ✅ Test button
- ✅ Auto-saves preferences
- ✅ Matches your theme (customizable CSS variables)

**Customize colors:**
```css
:root {
  --notif-primary: #your-brand-color;
  --notif-bg: #your-bg-color;
  /* See settings-panel.html for all variables */
}
```

---

## ⚙️ Option 2: JSON Configuration

**Best for:** Developers who prefer config files

**Step 1:** Create `notification-config.json`:
```json
{
  "notifications": {
    "enabled": true,
    "soundPath": "./sounds",
    "soundName": "level3",
    "volume": 0.7,
    "cooldownMs": 3000,
    "showEnablePrompt": true,
    "debug": false
  }
}
```

**Step 2:** Use the config loader:
```html
<script src="./howler.min.js"></script>
<script src="./notification.js"></script>
<script src="./config-loader.js"></script>

<script>
  let notifier = null;
  
  // One-liner initialization from config
  window.addEventListener('DOMContentLoaded', async () => {
    notifier = await initNotificationsFromConfig('./notification-config.json');
    console.log('✅ Notifications ready');
  });
</script>
```

**Configuration options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable notifications |
| `soundPath` | string | `"./sounds"` | Path to sounds directory |
| `soundName` | string | `"level3"` | Intensity: `level1` - `level5` |
| `volume` | number | `0.7` | Volume: 0.0 (silent) to 1.0 (max) |
| `cooldownMs` | number | `3000` | Min milliseconds between notifications |
| `showEnablePrompt` | boolean | `true` | Show browser autoplay prompt |
| `debug` | boolean | `false` | Enable console logging |

**Sound intensity levels:**
- `level1` - Whisper (most subtle)
- `level2` - Soft (gentle)
- `level3` - Medium (recommended)
- `level4` - Loud (attention-getting)
- `level5` - Very Loud (impossible to miss)

---

## 💻 Option 3: Programmatic Setup

**Best for:** Developers who want full control

```html
<script src="./howler.min.js"></script>
<script src="./notification.js"></script>

<script>
  let notifier = null;
  
  window.addEventListener('DOMContentLoaded', async () => {
    // Create with options
    notifier = new WebchatNotifications({
      soundPath: './sounds',
      soundName: 'level3',
      defaultVolume: 0.7,
      cooldownMs: 3000,
      debug: false
    });
    
    // Initialize
    await notifier.init();
    
    // Hook into your message system
    yourChat.on('message', (msg) => {
      // Change intensity based on message type
      if (msg.isMention) {
        notifier.setSound('level5');  // Loudest for mentions
      } else if (msg.isDM) {
        notifier.setSound('level4');  // Loud for DMs
      } else {
        notifier.setSound('level2');  // Soft for regular messages
      }
      
      notifier.notify();
    });
  });
</script>
```

**Available methods:**
```javascript
// Control notifications
notifier.notify();              // Trigger notification (only if tab hidden)
notifier.test();                // Play sound now (ignore tab state)
notifier.setEnabled(true);      // Enable notifications
notifier.setEnabled(false);     // Disable notifications

// Configure sound & volume
notifier.setSound('level1');    // Change intensity level
notifier.setVolume(0.5);        // Set volume (0.0 - 1.0)

// Get current settings
const settings = notifier.getSettings();
// Returns: { enabled, volume, soundName, isMobile, initialized }
```

---

## 🎨 Custom Settings UI

Don't like the default panel? Build your own:

```html
<!-- Enable/Disable -->
<label>
  <input type="checkbox" id="enable-notif" checked 
         onchange="notifier.setEnabled(this.checked)">
  Enable Notifications
</label>

<!-- Sound Selection -->
<select id="sound-select" onchange="notifier.setSound(this.value)">
  <option value="level1">🔕 Whisper</option>
  <option value="level2">🔔 Soft</option>
  <option value="level3" selected>🔔 Medium</option>
  <option value="level4">🔊 Loud</option>
  <option value="level5">📢 Very Loud</option>
</select>

<!-- Volume -->
<input type="range" min="0" max="100" value="70"
       oninput="notifier.setVolume(this.value / 100)">

<!-- Test -->
<button onclick="notifier.test()">Test Sound</button>
```

---

## 📱 Mobile Considerations

**iOS/Safari limitations:**
- Requires user gesture for EACH audio play
- May not work in background tabs
- Consider visual fallbacks (flashing favicon, badge count)

**Detect mobile:**
```javascript
const settings = notifier.getSettings();
if (settings.isMobile) {
  console.log('Mobile detected - audio may be limited');
  // Use visual notifications as fallback
}
```

---

## 🔧 Troubleshooting

### No sound playing?

**1. Check browser console for errors**
```javascript
// Enable debug mode
const notifier = new WebchatNotifications({ debug: true });
```

**2. Verify tab is hidden**
- Notifications only play when tab is in background
- Use `notifier.test()` to play regardless of tab state

**3. Check volume**
```javascript
const settings = notifier.getSettings();
console.log('Volume:', settings.volume);  // Should be > 0
notifier.setVolume(1.0);  // Try max volume
```

**4. Test sound files**
- Open examples/audio-test.html to verify files load
- Check browser Network tab for 404 errors

### Settings not saving?

Settings are saved in localStorage. Check:
```javascript
// View saved settings
console.log(localStorage.getItem('webchat_notifications_enabled'));
console.log(localStorage.getItem('webchat_notifications_volume'));
console.log(localStorage.getItem('webchat_notifications_soundName'));
```

If localStorage is disabled (private browsing), settings won't persist.

---

## 🎯 Recommended Setup for Moltbot/Clawdbot

**1. Copy files to your webchat:**
```bash
cp client/howler.min.js /path/to/webchat/js/
cp client/notification.js /path/to/webchat/js/
cp client/settings-panel.html /path/to/webchat/
cp -r client/sounds /path/to/webchat/
```

**2. Add to your webchat HTML:**
```html
<!-- At the end of <body> -->
<script src="/js/howler.min.js"></script>
<script src="/js/notification.js"></script>

<script>
  let notifier = null;
  
  window.addEventListener('DOMContentLoaded', async () => {
    notifier = new WebchatNotifications({
      soundPath: '/sounds',
      soundName: 'level3'
    });
    await notifier.init();
    
    // Hook into socket/polling for new messages
    socket.on('message', () => notifier.notify());
  });
</script>
```

**3. Add settings panel to your UI:**
```html
<!-- In your settings menu/modal -->
<div id="notification-settings"></div>

<script>
  fetch('/settings-panel.html')
    .then(r => r.text())
    .then(html => {
      document.getElementById('notification-settings').innerHTML = html;
    });
</script>
```

**Done!** Users can now configure notifications themselves.

---

## 📦 File Size

Total download (first load):
- howler.min.js: 36KB
- notification.js: 10KB  
- settings-panel.html: 8KB
- All 5 sounds: 141KB
- **Total: ~195KB** (one-time, then cached)

Users only download once, then browser caches everything.

---

## 🔗 Links

- **Full Documentation:** [README.md](../README.md)
- **Integration Guide:** [integration.md](./integration.md)
- **Example:** [examples/easy-setup.html](../examples/easy-setup.html)
- **GitHub:** https://github.com/brokemac79/webchat-audio-notifications

---

**Questions?** Open an issue on GitHub!
