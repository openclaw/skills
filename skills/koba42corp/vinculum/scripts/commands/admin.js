/**
 * Admin commands for gun-sync
 * Handles /link logs, /link reset, /link destroy, /link debug
 */

const formatting = require('../utils/formatting');

/**
 * Show recent sync logs
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function showLogs(context) {
  const { syncState } = context;
  
  const logs = syncState?.logs || [];
  
  if (logs.length === 0) {
    return `📋 **Sync Logs**\n\nNo recent logs.`;
  }
  
  const lines = ['📋 **Sync Logs**', ''];
  
  logs.slice(-20).forEach(log => {
    const time = new Date(log.timestamp).toLocaleTimeString();
    const level = log.level === 'error' ? '❌' : 
                  log.level === 'warn' ? '⚠️' : 'ℹ️';
    lines.push(`${time} ${level} ${log.message}`);
  });
  
  return lines.join('\n');
}

/**
 * Reset sync state (keep namespace)
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function reset(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return formatting.formatError(`Not connected to any network.`);
  }
  
  // Clear sync state
  if (syncState) {
    syncState.lastPush = null;
    syncState.lastPull = null;
    syncState.logs = [];
  }
  
  // Reconnect adapter
  if (adapter.connected) {
    await adapter.disconnect();
    await adapter.connect(config.namespace, config.encryption_key, {
      name: config.agent_name || 'Clawdbot',
      instanceId: context.instanceId,
      owner: context.owner,
      channel: context.channel
    });
  }
  
  return formatting.formatSuccess(
    `Sync state reset.\n\n` +
    `• Local cache cleared\n` +
    `• Connection refreshed\n` +
    `• Namespace preserved: \`${config.namespace}\``
  );
}

/**
 * Completely destroy namespace and all data
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function destroy(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return formatting.formatError(`Not connected to any network.`);
  }
  
  const oldNamespace = config.namespace;
  
  // Disconnect
  if (adapter.connected) {
    await adapter.disconnect();
  }
  
  // Clear all config
  await configManager.set({
    enabled: false,
    namespace: null,
    encryption_key: null
  });
  
  // Clear sync state
  if (syncState) {
    syncState.lastPush = null;
    syncState.lastPull = null;
    syncState.logs = [];
  }
  
  return `🗑️ **Namespace Destroyed**

Removed namespace: \`${oldNamespace}\`

• Local config cleared
• Disconnected from network
• Local Gun data may still exist in cache

Note: Other bots may still have copies of shared data.
Use \`/link init\` to create a new network.`;
}

/**
 * Show debug information
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function debug(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  const lines = ['🔧 **Debug Info**', ''];
  
  // Config
  lines.push('**Configuration**');
  lines.push(`Enabled: ${config.enabled}`);
  lines.push(`Namespace: ${config.namespace || 'none'}`);
  lines.push(`Agent: ${config.agent_name || 'Clawdbot'}`);
  lines.push(`Sync interval: ${config.sync_interval || 30}s`);
  lines.push('');
  
  // Adapter state
  lines.push('**Adapter**');
  lines.push(`Connected: ${adapter.connected}`);
  lines.push(`Agent ID: ${adapter.agentId || 'none'}`);
  lines.push(`Instance: ${context.instanceId}`);
  lines.push('');
  
  // Sync state
  lines.push('**Sync State**');
  lines.push(`Last push: ${syncState?.lastPush ? new Date(syncState.lastPush).toISOString() : 'never'}`);
  lines.push(`Last pull: ${syncState?.lastPull ? new Date(syncState.lastPull).toISOString() : 'never'}`);
  lines.push(`Log entries: ${syncState?.logs?.length || 0}`);
  lines.push('');
  
  // Network stats
  if (adapter.connected) {
    const stats = await adapter.getStats();
    const agents = await adapter.getAgents();
    
    lines.push('**Network**');
    lines.push(`Total agents: ${agents.length}`);
    lines.push(`Activity entries: ${stats.activityCount}`);
    lines.push(`Memory entries: ${stats.memoryCount}`);
    lines.push(`Decision entries: ${stats.decisionCount}`);
  }
  
  return lines.join('\n');
}

module.exports = {
  showLogs,
  reset,
  destroy,
  debug
};
