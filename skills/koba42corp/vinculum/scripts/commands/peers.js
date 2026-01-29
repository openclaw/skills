/**
 * Peers command for gun-sync
 * Handles /link peers
 */

const formatting = require('../utils/formatting');

/**
 * List connected peers
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function listPeers(context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` or \`/link join <code>\` first.`
    );
  }
  
  const agents = await adapter.getAgents();
  
  // Filter out self and format
  const peers = agents
    .filter(a => a.id !== context.instanceId)
    .map(a => ({
      name: a.identity?.name || a.id,
      online: a.status?.online || false,
      current_task: a.status?.current_task || null,
      last_seen: a.status?.updated || a.identity?.last_seen
    }));
  
  return formatting.formatPeerList(peers);
}

module.exports = {
  listPeers
};
