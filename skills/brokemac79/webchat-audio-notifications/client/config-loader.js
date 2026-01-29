/**
 * WebchatNotifications Config Loader
 * Load notification settings from JSON config file
 * 
 * Usage:
 * const config = await loadNotificationConfig('./config.json');
 * const notifier = new WebchatNotifications(config.notifications);
 */

async function loadNotificationConfig(configPath = './notification-config.json') {
  try {
    const response = await fetch(configPath);
    if (!response.ok) {
      throw new Error(`Config file not found: ${configPath}`);
    }
    
    const config = await response.json();
    
    // Validate config
    if (!config.notifications) {
      throw new Error('Config must have "notifications" object');
    }
    
    // Return just the notifications config
    return config.notifications;
  } catch (error) {
    console.error('Failed to load notification config:', error);
    console.log('Using default configuration');
    
    // Return defaults
    return {
      soundPath: './sounds',
      soundName: 'level3',
      defaultVolume: 0.7,
      cooldownMs: 3000,
      enableButton: true,
      debug: false
    };
  }
}

/**
 * Initialize notifications from config file
 * One-liner setup with JSON config
 * 
 * Usage:
 * const notifier = await initNotificationsFromConfig('./config.json');
 */
async function initNotificationsFromConfig(configPath = './notification-config.json') {
  const config = await loadNotificationConfig(configPath);
  const notifier = new WebchatNotifications(config);
  await notifier.init();
  return notifier;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadNotificationConfig,
    initNotificationsFromConfig
  };
}
