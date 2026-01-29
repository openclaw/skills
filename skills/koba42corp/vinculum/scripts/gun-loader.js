/**
 * Gun.js loader for Clawdbot gun-sync skill
 * 
 * Loads Gun through its proper entry point (gun/index.js -> gun/lib/server.js)
 * Suppresses verbose startup messages.
 */

const path = require('path');

// Suppress Gun's welcome and multicast messages
const originalLog = console.log;
console.log = function(...args) {
  if (args[0] && typeof args[0] === 'string') {
    if (args[0].includes('Hello wonderful person') ||
        args[0].includes('AXE relay') ||
        args[0].includes('Multicast on') ||
        args[0].includes('Warning: No localStorage')) {
      return; // Suppress
    }
  }
  originalLog.apply(console, args);
};

// Load Gun - use explicit path to ensure proper module resolution
const Gun = require(path.join(__dirname, '..', 'node_modules', 'gun'));

module.exports = Gun;
