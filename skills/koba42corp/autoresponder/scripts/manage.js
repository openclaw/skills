#!/usr/bin/env node

/**
 * iMessage Auto-Responder Config Manager
 * CLI for managing watch list
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const WORKSPACE = process.env.CLAWD_WORKSPACE || path.join(os.homedir(), 'clawd');
const CONFIG_PATH = path.join(WORKSPACE, 'imsg-autoresponder.json');

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return {
      enabled: true,
      watchList: [],
      defaultMinMinutesBetweenReplies: 15
    };
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  console.log('✓ Config saved to', CONFIG_PATH);
}

function showUsage() {
  console.log(`
iMessage Auto-Responder Manager

Usage:
  node manage.js list                           List all watch list entries
  node manage.js add <number> <prompt>          Add a contact to watch list
  node manage.js remove <number>                Remove a contact
  node manage.js enable <number>                Enable auto-responses for contact
  node manage.js disable <number>               Disable auto-responses for contact
  node manage.js set-delay <number> <minutes>   Set min minutes between replies
  node manage.js toggle                         Enable/disable entire system
  
  Bulk Operations:
  node manage.js set-all-delays <minutes>       Set delay for all contacts
  node manage.js enable-all                     Enable all contacts
  node manage.js disable-all                    Disable all contacts
  
  Time Windows:
  node manage.js set-time-window <number> <start> <end>   Add time window (HH:MM format)
  node manage.js clear-time-windows <number>              Remove all time windows
  
  Keyword Triggers:
  node manage.js add-keyword <number> <keyword>           Add keyword trigger
  node manage.js remove-keyword <number> <keyword>        Remove keyword trigger
  node manage.js clear-keywords <number>                  Remove all keyword triggers
  
  Daily Cap:
  node manage.js set-daily-cap <number> <max>             Set max replies per day (0 = unlimited)

Examples:
  node manage.js add "+15551234567" "Reply with a middle finger emoji"
  node manage.js add "+15559876543" "You are my helpful assistant. Reply warmly and briefly."
  node manage.js set-delay "+15551234567" 30
  node manage.js disable "+15551234567"
  node manage.js set-all-delays 30
  node manage.js disable-all
  node manage.js set-time-window "+15551234567" 09:00 22:00
  node manage.js clear-time-windows "+15551234567"
  node manage.js add-keyword "+15551234567" urgent
  node manage.js add-keyword "+15551234567" help
  node manage.js clear-keywords "+15551234567"
  `);
}

function list() {
  const config = loadConfig();
  
  console.log('\n=== Auto-Responder Status ===');
  console.log(`System: ${config.enabled ? '✓ ENABLED' : '✗ DISABLED'}`);
  console.log(`Default delay: ${config.defaultMinMinutesBetweenReplies} minutes\n`);
  
  if (config.watchList.length === 0) {
    console.log('No contacts in watch list.');
    return;
  }
  
  console.log('=== Watch List ===\n');
  config.watchList.forEach((contact, i) => {
    const status = contact.enabled === false ? '✗ DISABLED' : '✓ enabled';
    const delay = contact.minMinutesBetweenReplies || config.defaultMinMinutesBetweenReplies;
    
    console.log(`[${i + 1}] ${contact.identifier} (${status})`);
    if (contact.name) console.log(`    Name: ${contact.name}`);
    console.log(`    Delay: ${delay} minutes`);
    if (contact.maxRepliesPerDay) {
      console.log(`    Daily Cap: ${contact.maxRepliesPerDay} replies/day`);
    }
    if (contact.timeWindows && contact.timeWindows.length > 0) {
      console.log(`    Time Windows:`);
      contact.timeWindows.forEach(w => {
        console.log(`      ${w.start} - ${w.end}`);
      });
    }
    if (contact.keywords && contact.keywords.length > 0) {
      console.log(`    Keywords: ${contact.keywords.join(', ')}`);
    }
    console.log(`    Prompt: ${contact.prompt}`);
    console.log();
  });
}

function add(identifier, prompt, name) {
  const config = loadConfig();
  
  // Check if already exists
  const existing = config.watchList.find(c => c.identifier === identifier);
  if (existing) {
    console.log(`✗ Contact ${identifier} already exists. Use 'remove' first or edit the config manually.`);
    return;
  }
  
  config.watchList.push({
    identifier,
    name: name || '',
    prompt,
    enabled: true
  });
  
  saveConfig(config);
  console.log(`✓ Added ${identifier} to watch list`);
}

function remove(identifier) {
  const config = loadConfig();
  const index = config.watchList.findIndex(c => c.identifier === identifier);
  
  if (index === -1) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  config.watchList.splice(index, 1);
  saveConfig(config);
  console.log(`✓ Removed ${identifier} from watch list`);
}

function setEnabled(identifier, enabled) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  contact.enabled = enabled;
  saveConfig(config);
  console.log(`✓ ${enabled ? 'Enabled' : 'Disabled'} ${identifier}`);
}

function setDelay(identifier, minutes) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  contact.minMinutesBetweenReplies = parseInt(minutes);
  saveConfig(config);
  console.log(`✓ Set delay to ${minutes} minutes for ${identifier}`);
}

function toggle() {
  const config = loadConfig();
  config.enabled = !config.enabled;
  saveConfig(config);
  console.log(`✓ Auto-responder ${config.enabled ? 'ENABLED' : 'DISABLED'}`);
}

function setAllDelays(minutes) {
  const config = loadConfig();
  
  if (config.watchList.length === 0) {
    console.log('✗ No contacts in watch list');
    return;
  }
  
  config.watchList.forEach(contact => {
    contact.minMinutesBetweenReplies = parseInt(minutes);
  });
  
  saveConfig(config);
  console.log(`✓ Set delay to ${minutes} minutes for all ${config.watchList.length} contacts`);
}

function enableAll() {
  const config = loadConfig();
  
  if (config.watchList.length === 0) {
    console.log('✗ No contacts in watch list');
    return;
  }
  
  config.watchList.forEach(contact => {
    contact.enabled = true;
  });
  
  saveConfig(config);
  console.log(`✓ Enabled all ${config.watchList.length} contacts`);
}

function disableAll() {
  const config = loadConfig();
  
  if (config.watchList.length === 0) {
    console.log('✗ No contacts in watch list');
    return;
  }
  
  config.watchList.forEach(contact => {
    contact.enabled = false;
  });
  
  saveConfig(config);
  console.log(`✓ Disabled all ${config.watchList.length} contacts`);
}

function setTimeWindow(identifier, start, end) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  // Validate time format (HH:MM)
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
  if (!timeRegex.test(start) || !timeRegex.test(end)) {
    console.log('✗ Invalid time format. Use HH:MM (e.g., 09:00, 22:30)');
    return;
  }
  
  if (!contact.timeWindows) {
    contact.timeWindows = [];
  }
  
  contact.timeWindows.push({ start, end });
  saveConfig(config);
  console.log(`✓ Added time window ${start} - ${end} for ${identifier}`);
}

function clearTimeWindows(identifier) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  contact.timeWindows = [];
  saveConfig(config);
  console.log(`✓ Cleared all time windows for ${identifier}`);
}

function addKeyword(identifier, keyword) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  if (!contact.keywords) {
    contact.keywords = [];
  }
  
  if (contact.keywords.includes(keyword)) {
    console.log(`✗ Keyword "${keyword}" already exists for ${identifier}`);
    return;
  }
  
  contact.keywords.push(keyword);
  saveConfig(config);
  console.log(`✓ Added keyword "${keyword}" for ${identifier}`);
}

function removeKeyword(identifier, keyword) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  if (!contact.keywords || contact.keywords.length === 0) {
    console.log(`✗ No keywords configured for ${identifier}`);
    return;
  }
  
  const index = contact.keywords.indexOf(keyword);
  if (index === -1) {
    console.log(`✗ Keyword "${keyword}" not found for ${identifier}`);
    return;
  }
  
  contact.keywords.splice(index, 1);
  saveConfig(config);
  console.log(`✓ Removed keyword "${keyword}" from ${identifier}`);
}

function clearKeywords(identifier) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  contact.keywords = [];
  saveConfig(config);
  console.log(`✓ Cleared all keywords for ${identifier}`);
}

function setDailyCap(identifier, maxReplies) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    console.log(`✗ Contact ${identifier} not found in watch list`);
    return;
  }
  
  const max = parseInt(maxReplies);
  if (isNaN(max) || max < 0) {
    console.log(`✗ Invalid max replies value. Must be a positive number.`);
    return;
  }
  
  if (max === 0) {
    delete contact.maxRepliesPerDay;
    console.log(`✓ Removed daily cap for ${identifier} (unlimited)`);
  } else {
    contact.maxRepliesPerDay = max;
    console.log(`✓ Set daily cap to ${max} replies for ${identifier}`);
  }
  
  saveConfig(config);
}

// Parse command line
const [,, command, ...args] = process.argv;

switch (command) {
  case 'list':
    list();
    break;
    
  case 'add':
    if (args.length < 2) {
      console.log('✗ Usage: node manage.js add <number> "<prompt>" [name]');
      process.exit(1);
    }
    add(args[0], args[1], args[2]);
    break;
    
  case 'remove':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js remove <number>');
      process.exit(1);
    }
    remove(args[0]);
    break;
    
  case 'enable':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js enable <number>');
      process.exit(1);
    }
    setEnabled(args[0], true);
    break;
    
  case 'disable':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js disable <number>');
      process.exit(1);
    }
    setEnabled(args[0], false);
    break;
    
  case 'set-delay':
    if (args.length < 2) {
      console.log('✗ Usage: node manage.js set-delay <number> <minutes>');
      process.exit(1);
    }
    setDelay(args[0], args[1]);
    break;
    
  case 'toggle':
    toggle();
    break;
    
  case 'set-all-delays':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js set-all-delays <minutes>');
      process.exit(1);
    }
    setAllDelays(args[0]);
    break;
    
  case 'enable-all':
    enableAll();
    break;
    
  case 'disable-all':
    disableAll();
    break;
    
  case 'set-time-window':
    if (args.length < 3) {
      console.log('✗ Usage: node manage.js set-time-window <number> <start> <end>');
      console.log('  Example: node manage.js set-time-window "+15551234567" 09:00 22:00');
      process.exit(1);
    }
    setTimeWindow(args[0], args[1], args[2]);
    break;
    
  case 'clear-time-windows':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js clear-time-windows <number>');
      process.exit(1);
    }
    clearTimeWindows(args[0]);
    break;
    
  case 'add-keyword':
    if (args.length < 2) {
      console.log('✗ Usage: node manage.js add-keyword <number> <keyword>');
      console.log('  Example: node manage.js add-keyword "+15551234567" urgent');
      process.exit(1);
    }
    addKeyword(args[0], args[1]);
    break;
    
  case 'remove-keyword':
    if (args.length < 2) {
      console.log('✗ Usage: node manage.js remove-keyword <number> <keyword>');
      process.exit(1);
    }
    removeKeyword(args[0], args[1]);
    break;
    
  case 'clear-keywords':
    if (args.length < 1) {
      console.log('✗ Usage: node manage.js clear-keywords <number>');
      process.exit(1);
    }
    clearKeywords(args[0]);
    break;
    
  case 'set-daily-cap':
    if (args.length < 2) {
      console.log('✗ Usage: node manage.js set-daily-cap <number> <max_replies>');
      console.log('  Set to 0 for unlimited');
      process.exit(1);
    }
    setDailyCap(args[0], args[1]);
    break;
    
  default:
    showUsage();
    process.exit(command ? 1 : 0);
}
