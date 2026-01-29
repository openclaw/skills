/**
 * WebchatNotifications - Browser audio notifications for Moltbot/Clawdbot
 * 
 * Features:
 * - Plays sound when new messages arrive
 * - Only plays when tab is in background
 * - Respects browser autoplay policies
 * - Mobile-friendly with graceful fallbacks
 * - User preferences via localStorage
 * 
 * @version 1.0.0
 * @license MIT
 */

class WebchatNotifications {
  constructor(options = {}) {
    this.options = {
      soundPath: options.soundPath || './sounds',
      soundName: options.soundName || 'level3', // level1 (subtle) through level5 (loudest)
      defaultVolume: options.defaultVolume || 0.7,
      cooldownMs: options.cooldownMs || 3000, // Don't ping more than once per 3s
      enableButton: options.enableButton !== false, // Show by default
      debug: options.debug || false,
      ...options
    };

    // State
    this.enabled = this._getPreference('enabled', true);
    this.volume = this._getPreference('volume', this.options.defaultVolume);
    this.options.soundName = this._getPreference('soundName', this.options.soundName);
    this.lastNotifyTime = 0;
    this.initialized = false;
    this.isMobile = this._detectMobile();
    this.enablePromptShown = false;

    // Sound instance (initialized after Howler loads)
    this.sound = null;
    
    this._log('WebchatNotifications initialized', {
      isMobile: this.isMobile,
      enabled: this.enabled,
      volume: this.volume
    });
  }

  /**
   * Initialize the notification system
   * Must be called after Howler.js is loaded
   */
  async init() {
    if (!window.Howl) {
      console.error('WebchatNotifications: Howler.js not loaded');
      return this;
    }

    this._initSound();

    // Check if we need to show enable prompt
    if (this.options.enableButton && this._needsPermission()) {
      this._log('Autoplay blocked, will show enable prompt on first notify');
    }
    
    this.initialized = true;
    this._log('Initialization complete');
    return this;
  }

  /**
   * Initialize Howler sound instance
   */
  _initSound() {
    let soundSrc;
    
    // Check if using custom uploaded sound
    if (this.options.soundName === 'custom') {
      const customSound = this.getCustomSound();
      if (customSound) {
        soundSrc = [customSound.dataUrl];
      } else {
        // Custom sound not found, fallback to default
        this._log('Custom sound not found, using level3');
        this.options.soundName = 'level3';
        soundSrc = [`${this.options.soundPath}/level3.mp3`];
      }
    } else {
      // Use built-in sound
      soundSrc = [`${this.options.soundPath}/${this.options.soundName}.mp3`];
    }
    
    this.sound = new Howl({
      src: soundSrc,
      volume: this.volume,
      html5: true, // Use HTML5 Audio for better mobile support
      onloaderror: (id, err) => {
        console.error('WebchatNotifications: Sound load error', err);
      },
      onplayerror: (id, err) => {
        this._log('Play error, attempting unlock', err);
        // Attempt to unlock on next user interaction
        this.sound.once('unlock', () => {
          this._log('Audio unlocked successfully');
        });
      }
    });

    this._log(`Sound initialized: ${this.options.soundName}`);
  }

  /**
   * Play notification sound
   * @param {string} eventType - Type of event (future use for different sounds)
   */
  notify(eventType = 'message') {
    if (!this.initialized) {
      this._log('notify() called before init()');
      return;
    }

    // Don't notify if disabled
    if (!this.enabled) {
      this._log('Notifications disabled, skipping');
      return;
    }

    // Don't notify if tab is visible
    if (!this._isTabHidden()) {
      this._log('Tab is visible, skipping notification');
      return;
    }

    // Cooldown check - prevent notification spam
    const now = Date.now();
    if (now - this.lastNotifyTime < this.options.cooldownMs) {
      this._log('Cooldown active, skipping notification');
      return;
    }

    // Show enable prompt if needed (one-time)
    if (this._needsPermission() && !this.enablePromptShown) {
      this._showEnablePrompt();
      return;
    }

    // Play sound
    try {
      this.sound.play();
      this.lastNotifyTime = now;
      this._log('Notification played');
    } catch (err) {
      console.error('WebchatNotifications: Play failed', err);
    }
  }

  /**
   * Enable or disable notifications
   * @param {boolean} enabled
   */
  setEnabled(enabled) {
    this.enabled = Boolean(enabled);
    this._setPreference('enabled', this.enabled);
    this._log('Notifications', this.enabled ? 'enabled' : 'disabled');
  }

  /**
   * Set notification volume
   * @param {number} volume - Volume level (0.0 to 1.0)
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, parseFloat(volume) || 0.7));
    if (this.sound) {
      this.sound.volume(this.volume);
    }
    this._setPreference('volume', this.volume);
    this._log('Volume set to', this.volume);
  }

  /**
   * Change notification sound
   * @param {string} soundName - Sound name ('level1-5' or 'custom')
   */
  setSound(soundName) {
    if (!this.initialized) {
      console.error('WebchatNotifications: Cannot change sound before initialization');
      return;
    }

    // Unload old sound
    if (this.sound) {
      this.sound.unload();
    }

    // Update sound name
    this.options.soundName = soundName;
    this._setPreference('soundName', soundName);

    // Reinitialize with new sound
    this._initSound();
    this._log('Sound changed to', soundName);
  }

  /**
   * Upload custom sound file
   * @param {File} file - Audio file from file input
   * @returns {Promise<boolean>} Success status
   */
  async uploadCustomSound(file) {
    if (!file) {
      console.error('WebchatNotifications: No file provided');
      return false;
    }

    // Check file type
    const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/webm'];
    if (!validTypes.includes(file.type)) {
      console.error('WebchatNotifications: Invalid file type. Supported: MP3, WAV, OGG, WebM');
      return false;
    }

    // Check file size (max 500KB)
    if (file.size > 500000) {
      console.error('WebchatNotifications: File too large (max 500KB)');
      return false;
    }

    try {
      // Convert to base64 data URL
      const dataUrl = await this._fileToDataUrl(file);
      
      // Store in localStorage
      this._setPreference('customSoundData', dataUrl);
      this._setPreference('customSoundName', file.name);
      
      this._log('Custom sound uploaded:', file.name);
      return true;
    } catch (err) {
      console.error('WebchatNotifications: Upload failed', err);
      return false;
    }
  }

  /**
   * Remove custom sound
   */
  removeCustomSound() {
    localStorage.removeItem('webchat_notifications_customSoundData');
    localStorage.removeItem('webchat_notifications_customSoundName');
    
    // If currently using custom sound, switch to default
    if (this.options.soundName === 'custom') {
      this.setSound('level3');
    }
    
    this._log('Custom sound removed');
  }

  /**
   * Get custom sound info
   * @returns {Object|null} Custom sound info or null
   */
  getCustomSound() {
    const data = this._getPreference('customSoundData', null);
    const name = this._getPreference('customSoundName', null);
    
    if (data && name) {
      return { name, dataUrl: data };
    }
    return null;
  }

  /**
   * Get current settings
   */
  getSettings() {
    return {
      enabled: this.enabled,
      volume: this.volume,
      soundName: this.options.soundName,
      isMobile: this.isMobile,
      initialized: this.initialized
    };
  }

  /**
   * Test notification (plays even if tab is visible)
   */
  test() {
    if (!this.initialized || !this.sound) {
      console.error('WebchatNotifications: Not initialized');
      return;
    }

    try {
      this.sound.play();
      this._log('Test notification played');
    } catch (err) {
      console.error('WebchatNotifications: Test play failed', err);
    }
  }

  // ==================== Private Methods ====================

  /**
   * Check if tab is currently hidden
   */
  _isTabHidden() {
    // Standard Page Visibility API
    if (typeof document.hidden !== 'undefined') {
      return document.hidden;
    }
    // Vendor prefixes for older browsers
    if (typeof document.webkitHidden !== 'undefined') {
      return document.webkitHidden;
    }
    if (typeof document.mozHidden !== 'undefined') {
      return document.mozHidden;
    }
    // Fallback: assume visible
    return false;
  }

  /**
   * Detect if running on mobile device
   */
  _detectMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
      .test(navigator.userAgent);
  }

  /**
   * Check if audio permission is needed (autoplay blocked)
   */
  _needsPermission() {
    if (!window.Howler || !Howler.ctx) {
      return false;
    }
    // AudioContext is suspended when autoplay is blocked
    return Howler.ctx.state === 'suspended';
  }

  /**
   * Show enable prompt for autoplay restrictions
   */
  _showEnablePrompt() {
    if (this.enablePromptShown) return;
    
    this.enablePromptShown = true;
    
    // Create a simple overlay prompt
    const overlay = document.createElement('div');
    overlay.id = 'webchat-notifications-prompt';
    overlay.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #2c3e50;
      color: white;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      max-width: 300px;
      animation: slideIn 0.3s ease-out;
    `;

    overlay.innerHTML = `
      <style>
        @keyframes slideIn {
          from { transform: translateX(400px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      </style>
      <div style="margin-bottom: 8px;">
        <strong>🔔 Enable Sound Notifications?</strong>
      </div>
      <div style="margin-bottom: 12px; font-size: 13px; opacity: 0.9;">
        Get notified when new messages arrive (only when tab is hidden)
      </div>
      <div style="display: flex; gap: 8px;">
        <button id="webchat-notify-enable" style="
          flex: 1;
          background: #3498db;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
        ">Enable</button>
        <button id="webchat-notify-dismiss" style="
          background: transparent;
          color: rgba(255,255,255,0.7);
          border: 1px solid rgba(255,255,255,0.3);
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
        ">Dismiss</button>
      </div>
    `;

    document.body.appendChild(overlay);

    // Enable button
    document.getElementById('webchat-notify-enable').addEventListener('click', async () => {
      try {
        // Resume audio context
        if (Howler.ctx && Howler.ctx.state === 'suspended') {
          await Howler.ctx.resume();
        }
        // Play test sound
        this.sound.play();
        this._log('Audio enabled via prompt');
        
        // Remove prompt
        overlay.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => overlay.remove(), 300);
      } catch (err) {
        console.error('WebchatNotifications: Enable failed', err);
      }
    });

    // Dismiss button
    document.getElementById('webchat-notify-dismiss').addEventListener('click', () => {
      this.setEnabled(false);
      overlay.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => overlay.remove(), 300);
      this._log('Notifications disabled via prompt');
    });

    // Auto-dismiss after 15 seconds
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        overlay.remove();
        this._log('Enable prompt auto-dismissed');
      }
    }, 15000);
  }

  /**
   * Get preference from localStorage
   */
  _getPreference(key, defaultValue) {
    try {
      const stored = localStorage.getItem(`webchat_notifications_${key}`);
      return stored !== null ? JSON.parse(stored) : defaultValue;
    } catch (err) {
      this._log('Error reading preference', key, err);
      return defaultValue;
    }
  }

  /**
   * Set preference in localStorage
   */
  _setPreference(key, value) {
    try {
      localStorage.setItem(`webchat_notifications_${key}`, JSON.stringify(value));
    } catch (err) {
      console.error('WebchatNotifications: Error saving preference', key, err);
    }
  }

  /**
   * Convert File to data URL
   * @private
   */
  _fileToDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * Debug logging
   */
  _log(...args) {
    if (this.options.debug) {
      console.log('[WebchatNotifications]', ...args);
    }
  }
}

// Export for module systems or global
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WebchatNotifications;
} else {
  window.WebchatNotifications = WebchatNotifications;
}
