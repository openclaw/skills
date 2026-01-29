/**
 * Toggle commands for gun-sync
 * Handles /link on, /link off, /link push, /link pull
 */

const formatting = require('../utils/formatting');

/**
 * Enable sync
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function enable(context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` to create one, or \`/link join <code>\` to join.`
    );
  }
  
  if (config.enabled && adapter.connected) {
    return formatting.formatSuccess(`Link is already enabled.`);
  }
  
  // Enable in config
  await configManager.set({ enabled: true });
  
  // Connect adapter if not connected
  if (!adapter.connected) {
    await adapter.connect(config.namespace, config.encryption_key, {
      name: config.agent_name || 'Clawdbot',
      instanceId: context.instanceId,
      owner: context.owner,
      channel: context.channel
    });
  }
  
  return formatting.formatSuccess(
    `Link enabled.\n\n` +
    `Your activity will now be shared with the network.`
  );
}

/**
 * Disable sync
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function disable(context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.enabled) {
    return formatting.formatSuccess(`Link is already disabled.`);
  }
  
  // Disable in config
  await configManager.set({ enabled: false });
  
  // Update status to offline but don't fully disconnect
  if (adapter.connected) {
    await adapter.updateAgentStatus({ online: false });
  }
  
  return formatting.formatSuccess(
    `Link disabled.\n\n` +
    `Your work won't be shared until re-enabled.\n` +
    `You'll still receive updates from other agents.`
  );
}

/**
 * Force push local changes
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function forcePush(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(`Not connected to any network.`);
  }
  
  // Update our status with current timestamp
  await adapter.updateAgentStatus({ 
    online: true,
    updated: Date.now()
  });
  
  // Update sync state
  if (syncState) {
    syncState.lastPush = Date.now();
  }
  
  return formatting.formatSuccess(
    `Pushed changes to network.\n\n` +
    `Status updated at ${new Date().toLocaleTimeString()}.`
  );
}

/**
 * Force pull remote changes
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function forcePull(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(`Not connected to any network.`);
  }
  
  // Get fresh data
  const agents = await adapter.getAgents();
  const activity = await adapter.getActivity(10);
  
  const peerCount = agents.filter(a => a.id !== context.instanceId).length;
  const activityCount = activity.length;
  
  // Update sync state
  if (syncState) {
    syncState.lastPull = Date.now();
  }
  
  return formatting.formatSuccess(
    `Pulled from network.\n\n` +
    `• ${peerCount} peer(s) found\n` +
    `• ${activityCount} recent activities`
  );
}

module.exports = {
  enable,
  disable,
  forcePush,
  forcePull
};
