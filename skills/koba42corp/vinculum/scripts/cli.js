#!/usr/bin/env node
/**
 * CLI wrapper for Vinculum skill
 * Usage: vinculum [command] [args]
 */

const vinculum = require('./index');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === 'help' || args[0] === '--help' || args[0] === '-h') {
    console.log(`
vinculum — Shared consciousness for Clawdbot

USAGE:
  vinculum [command] [options]

COMMANDS:
  init              Create a new collective
  join <code>       Join an existing collective
  invite            Generate invite code for current collective
  leave             Leave collective
  
  on                Enable link
  off               Disable link
  
  status            Show detailed status
  drones            List connected drones
  activity [drone]  Show recent activity
  decisions         Show shared decisions
  
  config            Show current config
  config <k> <v>    Set config value
  
  relay             Relay status
  relay start       Start Vinculum relay
  relay stop        Stop relay
  relay restart     Restart relay
  relay logs [n]    Show relay logs
  relay peer <url>  Add remote peer
  
  share "<note>"    Share a thought/memory
  
  logs              Show link logs
  debug             Debug info
  reset             Reset link state
  
EXAMPLES:
  vinculum relay start
  vinculum init
  vinculum join abc123
  vinculum drones
  vinculum share "Found a good solution for X"
`);
    process.exit(0);
  }
  
  // Convert CLI args to /link command format
  const command = '/link ' + args.join(' ');
  
  try {
    // Mock context for CLI usage
    const context = {
      instanceId: require('os').hostname() + '-cli',
      owner: process.env.USER || 'cli',
      channel: 'cli'
    };
    
    const result = await vinculum.handleCommand(command, context);
    console.log(result);
    
    // Give Gun time to sync before exiting
    await new Promise(r => setTimeout(r, 500));
    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
