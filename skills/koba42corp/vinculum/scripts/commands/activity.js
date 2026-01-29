/**
 * Activity commands for gun-sync
 * Handles /link activity, /link decisions, /link share
 */

const formatting = require('../utils/formatting');

/**
 * List recent activity
 * @param {string} agentFilter - Optional agent name to filter by
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function listActivity(agentFilter, context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` or \`/link join <code>\` first.`
    );
  }
  
  const activities = await adapter.getActivity(20, agentFilter || null);
  
  return formatting.formatActivityList(activities, agentFilter);
}

/**
 * List shared decisions
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function listDecisions(context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` or \`/link join <code>\` first.`
    );
  }
  
  const decisions = await adapter.getDecisions();
  
  return formatting.formatDecisionsList(decisions);
}

/**
 * Manually share a note/memory
 * @param {string} text - Text to share
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function shareNote(text, context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !adapter.connected) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` or \`/link join <code>\` first.`
    );
  }
  
  if (!text || text.trim().length === 0) {
    return formatting.formatError(
      `Missing text to share.\n\n` +
      `Usage: \`/link share "Your note here"\``
    );
  }
  
  // Share as memory entry
  await adapter.shareMemory({
    content: text.trim(),
    context: 'Manually shared via /link share',
    tags: ['manual', 'note']
  });
  
  return formatting.formatSuccess(
    `Shared to network:\n\n"${text.trim()}"`
  );
}

module.exports = {
  listActivity,
  listDecisions,
  shareNote
};
