# Integration Guide - Moltbot/Clawdbot Webchat

This guide explains how to integrate audio notifications into the Moltbot/Clawdbot webchat interface.

## Prerequisites

- Moltbot/Clawdbot webchat running
- Access to webchat HTML/JavaScript files
- Basic understanding of JavaScript events

## Integration Steps

### Step 1: Copy Files

Copy the notification files to your webchat directory:

```bash
# From the skill directory
cp client/howler.min.js /path/to/webchat/js/
cp client/notification.js /path/to/webchat/js/
cp -r client/sounds /path/to/webchat/
```

### Step 2: Load Scripts

Add to your webchat HTML (before closing `</body>`):

```html
<!-- Load Howler.js first -->
<script src="/js/howler.min.js"></script>

<!-- Load WebchatNotifications -->
<script src="/js/notification.js"></script>

<!-- Initialize -->
<script>
  let notifier = null;
  
  // Initialize on page load
  document.addEventListener('DOMContentLoaded', async () => {
    notifier = new WebchatNotifications({
      soundPath: '/sounds/notification',
      defaultVolume: 0.7,
      debug: false  // Set to true for development
    });
    
    await notifier.init();
    console.log('Webchat notifications ready');
  });
</script>
```

### Step 3: Hook Into Message Events

Find where your webchat receives new messages and add the notification trigger.

#### Example: WebSocket messages

```javascript
socket.on('message', (message) => {
  // Your existing message handling code
  displayMessage(message);
  
  // Trigger notification
  if (notifier && notifier.initialized) {
    notifier.notify('message');
  }
});
```

#### Example: Polling/AJAX

```javascript
async function checkForNewMessages() {
  const messages = await fetch('/api/messages').then(r => r.json());
  
  messages.forEach(msg => {
    if (isNewMessage(msg)) {
      displayMessage(msg);
      
      // Trigger notification
      if (notifier && notifier.initialized) {
        notifier.notify('message');
      }
    }
  });
}
```

#### Example: Event Bus

```javascript
// Subscribe to message events
eventBus.subscribe('webchat:newMessage', (data) => {
  if (notifier && notifier.initialized) {
    notifier.notify('message');
  }
});
```

### Step 4: Add User Controls (Optional)

Add UI controls for users to manage notifications:

```html
<!-- Settings panel -->
<div id="notification-settings">
  <h3>🔔 Notifications</h3>
  
  <!-- Enable/Disable -->
  <label>
    <input type="checkbox" id="notif-enabled" checked 
           onchange="notifier.setEnabled(this.checked)">
    Enable sound notifications
  </label>
  
  <!-- Volume slider -->
  <div>
    <label>Volume: <span id="notif-volume-value">70%</span></label>
    <input type="range" id="notif-volume" min="0" max="100" value="70"
           oninput="updateNotificationVolume(this.value)">
  </div>
  
  <!-- Test button -->
  <button onclick="notifier.test()">Test Sound</button>
</div>

<script>
  function updateNotificationVolume(value) {
    notifier.setVolume(value / 100);
    document.getElementById('notif-volume-value').textContent = value + '%';
  }
  
  // Restore settings on page load
  document.addEventListener('DOMContentLoaded', () => {
    const settings = notifier.getSettings();
    document.getElementById('notif-enabled').checked = settings.enabled;
    document.getElementById('notif-volume').value = Math.round(settings.volume * 100);
  });
</script>
```

### Step 5: Test

1. Open webchat in browser
2. Open browser console (F12)
3. Switch to another tab
4. Send a test message
5. You should hear a notification sound!

## Common Integration Patterns

### Pattern 1: Only notify for @mentions

```javascript
socket.on('message', (message) => {
  displayMessage(message);
  
  // Only notify if user is mentioned
  if (message.mentions && message.mentions.includes(currentUser.id)) {
    notifier.notify('mention');
  }
});
```

### Pattern 2: Different sounds for different events

```javascript
// Future enhancement - requires multiple sound files
socket.on('message', (msg) => {
  if (msg.type === 'mention') {
    notifier.notify('mention');
  } else if (msg.type === 'dm') {
    notifier.notify('dm');
  } else {
    notifier.notify('message');
  }
});
```

### Pattern 3: Respect Do Not Disturb hours

```javascript
function shouldNotify() {
  const hour = new Date().getHours();
  const isDND = hour < 7 || hour > 22;  // 10 PM - 7 AM
  return !isDND;
}

socket.on('message', (message) => {
  displayMessage(message);
  
  if (shouldNotify() && notifier.initialized) {
    notifier.notify();
  }
});
```

### Pattern 4: Notification badge + sound

```javascript
let unreadCount = 0;

socket.on('message', (message) => {
  displayMessage(message);
  
  // Update badge
  if (document.hidden) {
    unreadCount++;
    updateFaviconBadge(unreadCount);
    
    // Play sound
    notifier.notify();
  }
});

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    // User returned to tab - clear badge
    unreadCount = 0;
    updateFaviconBadge(0);
  }
});
```

## Configuration Options

### Development Mode

Enable debug logging during development:

```javascript
const notifier = new WebchatNotifications({
  debug: true  // Logs all events to console
});
```

### Custom Sound Files

Use your own notification sounds:

```javascript
const notifier = new WebchatNotifications({
  soundPath: '/assets/custom-notification',
  // Expects: /assets/custom-notification.mp3 (and .webm)
});
```

### Longer Cooldown

Prevent notification spam with longer cooldown:

```javascript
const notifier = new WebchatNotifications({
  cooldownMs: 10000  // 10 seconds between notifications
});
```

### Disable Enable Prompt

Hide the autoplay enable prompt (not recommended):

```javascript
const notifier = new WebchatNotifications({
  enableButton: false  // User must enable manually
});
```

## Moltbot-Specific Integration

### Integration Point 1: Main Chat Module

If Moltbot webchat uses a modular structure:

```javascript
// src/modules/chat.js
import WebchatNotifications from './notification.js';

class ChatModule {
  constructor() {
    this.notifier = null;
  }
  
  async init() {
    // Initialize notifier
    this.notifier = new WebchatNotifications({
      soundPath: '/sounds/notification',
      defaultVolume: 0.7
    });
    await this.notifier.init();
  }
  
  onNewMessage(message) {
    this.displayMessage(message);
    
    // Notify if tab is hidden
    if (this.notifier) {
      this.notifier.notify();
    }
  }
}
```

### Integration Point 2: Event Emitter Pattern

If Moltbot uses EventEmitter:

```javascript
// Hook into chat events
chatEmitter.on('message:received', (data) => {
  if (notifier && !data.fromSelf) {
    notifier.notify();
  }
});

chatEmitter.on('message:mention', (data) => {
  if (notifier) {
    notifier.notify('mention');
  }
});
```

### Integration Point 3: React/Vue Component

If webchat is built with a framework:

```javascript
// React example
import { useEffect, useState } from 'react';
import WebchatNotifications from './notification.js';

function Chat() {
  const [notifier, setNotifier] = useState(null);
  
  useEffect(() => {
    const n = new WebchatNotifications({
      soundPath: '/sounds/notification'
    });
    n.init().then(() => setNotifier(n));
    
    return () => {
      // Cleanup if needed
    };
  }, []);
  
  const handleNewMessage = (message) => {
    // Display message
    setMessages(prev => [...prev, message]);
    
    // Notify
    if (notifier) {
      notifier.notify();
    }
  };
  
  return (
    <div>
      {/* Chat UI */}
    </div>
  );
}
```

## Security Considerations

### Content Security Policy (CSP)

If your webchat uses CSP, ensure these directives:

```
Content-Security-Policy: 
  script-src 'self' 'unsafe-inline';
  media-src 'self';
```

### Local Storage

The notification system uses localStorage for preferences. Ensure it's not disabled:

```javascript
// Check if localStorage is available
if (typeof localStorage !== 'undefined') {
  // Safe to use WebchatNotifications
} else {
  console.warn('localStorage unavailable - notification preferences will not persist');
}
```

## Testing Checklist

- [ ] Script files load without errors (check Network tab)
- [ ] Sound files accessible (check Network tab)
- [ ] `notifier.init()` completes successfully
- [ ] Enable prompt appears if autoplay is blocked
- [ ] Sound plays when tab is hidden
- [ ] Sound does NOT play when tab is visible
- [ ] Volume slider works
- [ ] Enable/disable toggle works
- [ ] Preferences persist after page reload
- [ ] Works in Chrome, Firefox, Safari
- [ ] Mobile graceful degradation

## Rollback Plan

If you need to disable notifications quickly:

```javascript
// Disable globally
if (window.notifier) {
  notifier.setEnabled(false);
}

// Or remove the scripts
// Just comment out the <script> tags in HTML
```

## Performance Notes

- **Bundle size:** ~36KB (Howler.js) + 10KB (notification.js) + 76KB (sounds) = ~122KB total
- **Memory:** ~2MB during playback
- **CPU:** Negligible (audio handled by browser)
- **Network:** One-time download, then cached

## Support

- **Test page:** Open `examples/test.html` for debugging
- **Debug mode:** Set `debug: true` in constructor
- **Browser console:** Check for error messages
- **GitHub Issues:** Report bugs with browser version + console output

---

**Integration difficulty:** ⭐⭐☆☆☆ (Easy)  
**Estimated time:** 15-30 minutes  
**Last updated:** 2026-01-28
