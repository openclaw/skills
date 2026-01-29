/**
 * Config commands for gun-sync
 * Handles /link config
 */

const formatting = require('../utils/formatting');

/**
 * Show current configuration
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function showConfig(context) {
  const { configManager } = context;
  
  const config = await configManager.get();
  
  return formatting.formatConfig({
    shareActivity: config.share?.activity !== false,
    shareMemory: config.share?.memory !== false,
    shareDecisions: config.share?.decisions !== false,
    autoSync: config.auto_sync !== false,
    syncInterval: config.sync_interval || 30,
    agentName: config.agent_name || 'Clawdbot',
    namespaceId: config.namespace
  });
}

/**
 * Set a configuration value
 * @param {string} key - Config key (e.g., "share-activity")
 * @param {string} value - New value
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function setConfig(key, value, context) {
  const { configManager } = context;
  
  if (!key) {
    return showConfig(context);
  }
  
  const config = await configManager.get();
  
  // Normalize key
  const normalizedKey = key.toLowerCase().replace(/-/g, '_');
  
  // Handle different config keys
  switch (normalizedKey) {
    case 'share_activity':
      const shareActivity = parseBoolean(value);
      if (shareActivity === null) {
        return formatting.formatError(`Invalid value. Use \`on\` or \`off\`.`);
      }
      await configManager.set({ share: { ...config.share, activity: shareActivity } });
      return formatting.formatSuccess(
        `Activity sharing ${shareActivity ? 'enabled' : 'disabled'}.`
      );
    
    case 'share_memory':
      const shareMemory = parseBoolean(value);
      if (shareMemory === null) {
        return formatting.formatError(`Invalid value. Use \`on\` or \`off\`.`);
      }
      await configManager.set({ share: { ...config.share, memory: shareMemory } });
      return formatting.formatSuccess(
        `Memory sharing ${shareMemory ? 'enabled' : 'disabled'}.`
      );
    
    case 'share_decisions':
      const shareDecisions = parseBoolean(value);
      if (shareDecisions === null) {
        return formatting.formatError(`Invalid value. Use \`on\` or \`off\`.`);
      }
      await configManager.set({ share: { ...config.share, decisions: shareDecisions } });
      return formatting.formatSuccess(
        `Decision sharing ${shareDecisions ? 'enabled' : 'disabled'}.`
      );
    
    case 'auto_sync':
      const autoSync = parseBoolean(value);
      if (autoSync === null) {
        return formatting.formatError(`Invalid value. Use \`on\` or \`off\`.`);
      }
      await configManager.set({ auto_sync: autoSync });
      return formatting.formatSuccess(
        `Auto-sync ${autoSync ? 'enabled' : 'disabled'}.`
      );
    
    case 'sync_interval':
      const interval = parseInt(value, 10);
      if (isNaN(interval) || interval < 5 || interval > 3600) {
        return formatting.formatError(
          `Invalid interval. Must be between 5 and 3600 seconds.`
        );
      }
      await configManager.set({ sync_interval: interval });
      return formatting.formatSuccess(
        `Sync interval set to ${interval} seconds.`
      );
    
    case 'agent_name':
      if (!value || value.trim().length === 0) {
        return formatting.formatError(`Agent name cannot be empty.`);
      }
      await configManager.set({ agent_name: value.trim() });
      return formatting.formatSuccess(
        `Agent name set to "${value.trim()}".`
      );
    
    default:
      return formatting.formatError(
        `Unknown config key: \`${key}\`\n\n` +
        `Available keys:\n` +
        `• \`share-activity\` — on/off\n` +
        `• \`share-memory\` — on/off\n` +
        `• \`share-decisions\` — on/off\n` +
        `• \`auto-sync\` — on/off\n` +
        `• \`sync-interval\` — seconds (5-3600)\n` +
        `• \`agent-name\` — display name`
      );
  }
}

/**
 * Parse a boolean-ish value
 * @param {string} value
 * @returns {boolean|null}
 */
function parseBoolean(value) {
  if (!value) return null;
  const v = value.toLowerCase();
  if (['on', 'true', 'yes', '1', 'enabled'].includes(v)) return true;
  if (['off', 'false', 'no', '0', 'disabled'].includes(v)) return false;
  return null;
}

module.exports = {
  showConfig,
  setConfig
};
