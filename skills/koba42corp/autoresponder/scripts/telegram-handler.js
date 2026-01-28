#!/usr/bin/env node

/**
 * Telegram Command Handler for iMessage Auto-Responder
 * Wraps manage.js operations for Telegram bot integration
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const WORKSPACE = process.env.CLAWD_WORKSPACE || path.join(os.homedir(), 'clawd');
const CONFIG_PATH = path.join(WORKSPACE, 'imsg-autoresponder.json');
const STATE_PATH = path.join(WORKSPACE, 'data', 'imsg-autoresponder-state.json');
const LOG_PATH = path.join(WORKSPACE, 'logs', 'imsg-autoresponder.log');
const MANAGE_SCRIPT = path.join(__dirname, 'manage.js');

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return { enabled: true, watchList: [], defaultMinMinutesBetweenReplies: 15 };
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

function loadState() {
  if (!fs.existsSync(STATE_PATH)) {
    return { lastResponses: {}, lastChecked: {}, processing: {} };
  }
  return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
}

function getWatcherStatus() {
  const pidFile = path.join(WORKSPACE, 'data', 'imsg-autoresponder.pid');
  
  if (!fs.existsSync(pidFile)) {
    return { running: false };
  }
  
  const pid = fs.readFileSync(pidFile, 'utf8').trim();
  
  try {
    process.kill(parseInt(pid), 0); // Check if process exists
    return { running: true, pid: parseInt(pid) };
  } catch (e) {
    return { running: false, stale: true };
  }
}

function formatContact(contact, index, state) {
  const status = contact.enabled === false ? '❌' : '✅';
  const delay = contact.minMinutesBetweenReplies !== undefined 
    ? contact.minMinutesBetweenReplies 
    : 15;
  
  const lastResponse = state.lastResponses[contact.identifier];
  const lastResponseStr = lastResponse 
    ? `\n   Last response: ${new Date(lastResponse).toLocaleString()}`
    : '';
  
  // Statistics
  const stats = state.stats && state.stats[contact.identifier];
  const statsStr = stats 
    ? `\n   📊 Total: ${stats.totalResponses} | Today: ${stats.dailyCount}`
    : '';
  
  const promptPreview = contact.prompt.length > 80 
    ? contact.prompt.substring(0, 80) + '...'
    : contact.prompt;
  
  return `**[${index + 1}] ${contact.name || 'Unnamed'}** ${status}
   📞 \`${contact.identifier}\`
   ⏱️ Delay: ${delay} min
   💬 Prompt: _${promptPreview}_${lastResponseStr}${statsStr}`;
}

function handleList() {
  const config = loadConfig();
  const state = loadState();
  const watcherStatus = getWatcherStatus();
  
  const statusEmoji = config.enabled ? '✅' : '❌';
  const watcherEmoji = watcherStatus.running ? '🟢' : '🔴';
  
  let output = `**📱 iMessage Auto-Responder**\n\n`;
  output += `System: ${statusEmoji} ${config.enabled ? 'ENABLED' : 'DISABLED'}\n`;
  output += `Watcher: ${watcherEmoji} ${watcherStatus.running ? `Running (PID ${watcherStatus.pid})` : 'Stopped'}\n`;
  output += `Default delay: ${config.defaultMinMinutesBetweenReplies} minutes\n\n`;
  
  if (config.watchList.length === 0) {
    output += '📭 No contacts in watch list.';
  } else {
    output += `**👥 Watch List (${config.watchList.length})**\n\n`;
    config.watchList.forEach((contact, i) => {
      output += formatContact(contact, i, state) + '\n\n';
    });
  }
  
  return output;
}

function handleAdd(identifier, name, prompt) {
  execSync(`node "${MANAGE_SCRIPT}" add "${identifier}" "${prompt}" "${name}"`, {
    stdio: 'inherit'
  });
  return `✅ Added **${name}** (\`${identifier}\`) to watch list.\n\nRestart watcher to apply changes.`;
}

function handleRemove(identifier) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  const name = contact ? contact.name : identifier;
  
  execSync(`node "${MANAGE_SCRIPT}" remove "${identifier}"`, {
    stdio: 'inherit'
  });
  return `✅ Removed **${name}** (\`${identifier}\`) from watch list.\n\nRestart watcher to apply changes.`;
}

function handleEdit(identifier, newPrompt) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    return `❌ Contact \`${identifier}\` not found in watch list.`;
  }
  
  contact.prompt = newPrompt;
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  
  return `✅ Updated prompt for **${contact.name}** (\`${identifier}\`).\n\nRestart watcher to apply changes.`;
}

function handleDelay(identifier, minutes) {
  execSync(`node "${MANAGE_SCRIPT}" set-delay "${identifier}" ${minutes}`, {
    stdio: 'inherit'
  });
  
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  const name = contact ? contact.name : identifier;
  
  return `✅ Set delay to **${minutes} minutes** for **${name}** (\`${identifier}\`).\n\nRestart watcher to apply changes.`;
}

function handleToggle() {
  execSync(`node "${MANAGE_SCRIPT}" toggle`, {
    stdio: 'inherit'
  });
  
  const config = loadConfig();
  return config.enabled 
    ? '✅ Auto-responder **ENABLED**.\n\nRestart watcher to apply changes.'
    : '⏸️ Auto-responder **DISABLED**.\n\nRestart watcher to apply changes.';
}

function handleStatus() {
  const watcherStatus = getWatcherStatus();
  const config = loadConfig();
  
  let output = `**📊 Auto-Responder Status**\n\n`;
  
  if (watcherStatus.running) {
    output += `🟢 **Watcher is RUNNING** (PID ${watcherStatus.pid})\n\n`;
    
    // Get recent log entries
    if (fs.existsSync(LOG_PATH)) {
      const logs = execSync(`tail -10 "${LOG_PATH}"`, { encoding: 'utf8' });
      output += `**Recent Activity:**\n\`\`\`\n${logs}\`\`\``;
    }
  } else {
    output += `🔴 **Watcher is STOPPED**\n\n`;
    if (watcherStatus.stale) {
      output += `⚠️ Stale PID file detected. Run restart to clean up.`;
    }
  }
  
  return output;
}

function handleHistory(identifier, limit = 10) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    return `❌ Contact \`${identifier}\` not found in watch list.`;
  }
  
  const name = contact.name || identifier;
  
  // Parse logs for this contact
  if (!fs.existsSync(LOG_PATH)) {
    return `📭 No history found for **${name}**.`;
  }
  
  const logs = fs.readFileSync(LOG_PATH, 'utf8');
  const lines = logs.split('\n').filter(line => 
    line.includes(identifier) || line.includes(name)
  ).slice(-limit * 3); // Get more lines, then filter
  
  const responses = [];
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('Generated response:')) {
      const response = lines[i].split('Generated response: ')[1];
      const timestamp = lines[i].match(/\[(.*?)\]/)?.[1];
      if (response) {
        responses.push({ timestamp, response });
      }
    }
  }
  
  let output = `**💬 Recent Responses to ${name}**\n\n`;
  
  if (responses.length === 0) {
    output += `📭 No responses found yet.`;
  } else {
    responses.slice(-limit).forEach(({ timestamp, response }) => {
      const date = new Date(timestamp).toLocaleString();
      output += `**${date}**\n${response}\n\n`;
    });
  }
  
  return output;
}

async function generateTestResponse(contact, testMessage) {
  const prompt = `${contact.prompt}

Context - Recent message history (newest first):
(No history - test mode)

Latest message from ${contact.name || contact.identifier}:
${testMessage}

Generate a response now:`;

  // Get OpenAI API key from Clawdbot config
  const configPath = path.join(os.homedir(), '.clawdbot', 'clawdbot.json');
  let apiKey = process.env.OPENAI_API_KEY;
  
  if (!apiKey && fs.existsSync(configPath)) {
    try {
      const clawdbotConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      apiKey = clawdbotConfig.skills?.['openai-whisper-api']?.apiKey || clawdbotConfig.skills?.['openai-image-gen']?.apiKey;
    } catch (e) {
      // Ignore config parse errors
    }
  }

  if (!apiKey) {
    throw new Error('OPENAI_API_KEY not found');
  }

  const payload = JSON.stringify({
    model: 'gpt-4',
    messages: [{ role: 'user', content: prompt }],
    max_tokens: 150,
    temperature: 0.9
  });

  return new Promise((resolve, reject) => {
    const proc = spawn('curl', [
      '-s',
      'https://api.openai.com/v1/chat/completions',
      '-H', 'Content-Type: application/json',
      '-H', `Authorization: Bearer ${apiKey}`,
      '-d', payload
    ]);

    let output = '';

    proc.stdout.on('data', (data) => {
      output += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`OpenAI API call failed`));
        return;
      }

      try {
        const response = JSON.parse(output);
        if (response.error) {
          reject(new Error(`OpenAI API error: ${response.error.message}`));
          return;
        }
        
        const text = response.choices[0].message.content.trim();
        resolve(text);
      } catch (e) {
        reject(new Error(`Failed to parse OpenAI response: ${e.message}`));
      }
    });
  });
}

async function handleTest(identifier, testMessage) {
  const config = loadConfig();
  const contact = config.watchList.find(c => c.identifier === identifier);
  
  if (!contact) {
    return `❌ Contact \`${identifier}\` not found in watch list.`;
  }
  
  const name = contact.name || identifier;
  
  try {
    const response = await generateTestResponse(contact, testMessage);
    
    return `🧪 **Test Mode: ${name}**\n\n` +
      `**Test Message:**\n_"${testMessage}"_\n\n` +
      `**Generated Response:**\n${response}\n\n` +
      `✅ This response was **NOT sent**. This is preview only.`;
  } catch (error) {
    return `🧪 **Test Mode: ${name}**\n\n` +
      `**Test Message:**\n_"${testMessage}"_\n\n` +
      `❌ Failed to generate response:\n${error.message}`;
  }
}

function handleRestart() {
  const launcherPath = path.join(__dirname, 'launcher.sh');
  
  try {
    execSync(`"${launcherPath}" restart`, { encoding: 'utf8' });
    return '✅ Watcher restarted successfully.';
  } catch (e) {
    return `❌ Failed to restart watcher:\n\`\`\`\n${e.message}\`\`\``;
  }
}

function handleSetAllDelays(minutes) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" set-all-delays ${minutes}`, { encoding: 'utf8' });
    return `✅ Set delay to **${minutes} minutes** for all contacts.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to set delays:\n${e.message}`;
  }
}

function handleEnableAll() {
  try {
    execSync(`node "${MANAGE_SCRIPT}" enable-all`, { encoding: 'utf8' });
    return `✅ Enabled all contacts.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to enable all:\n${e.message}`;
  }
}

function handleDisableAll() {
  try {
    execSync(`node "${MANAGE_SCRIPT}" disable-all`, { encoding: 'utf8' });
    return `✅ Disabled all contacts.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to disable all:\n${e.message}`;
  }
}

function handleSetTimeWindow(identifier, start, end) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" set-time-window "${identifier}" "${start}" "${end}"`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    return `✅ Added time window **${start} - ${end}** for ${name}.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to set time window:\n${e.message}`;
  }
}

function handleClearTimeWindows(identifier) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" clear-time-windows "${identifier}"`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    return `✅ Cleared all time windows for ${name}.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to clear time windows:\n${e.message}`;
  }
}

function handleAddKeyword(identifier, keyword) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" add-keyword "${identifier}" "${keyword}"`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    return `✅ Added keyword **"${keyword}"** for ${name}.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to add keyword:\n${e.message}`;
  }
}

function handleRemoveKeyword(identifier, keyword) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" remove-keyword "${identifier}" "${keyword}"`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    return `✅ Removed keyword **"${keyword}"** from ${name}.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to remove keyword:\n${e.message}`;
  }
}

function handleClearKeywords(identifier) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" clear-keywords "${identifier}"`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    return `✅ Cleared all keywords for ${name}.\n\nRestart watcher to apply changes.`;
  } catch (e) {
    return `❌ Failed to clear keywords:\n${e.message}`;
  }
}

function handleStats(identifier) {
  const config = loadConfig();
  const state = loadState();
  
  if (identifier) {
    // Show stats for specific contact
    const contact = config.watchList.find(c => c.identifier === identifier);
    if (!contact) {
      return `❌ Contact \`${identifier}\` not found in watch list.`;
    }
    
    const name = contact.name || identifier;
    const stats = state.stats && state.stats[identifier];
    
    if (!stats || stats.totalResponses === 0) {
      return `📊 **Stats for ${name}**\n\nNo responses sent yet.`;
    }
    
    const firstDate = new Date(stats.firstResponse).toLocaleString();
    const lastDate = new Date(stats.lastResponse).toLocaleString();
    const daysSince = Math.floor((Date.now() - stats.firstResponse) / (1000 * 60 * 60 * 24));
    const avgPerDay = daysSince > 0 ? (stats.totalResponses / daysSince).toFixed(1) : stats.totalResponses;
    
    return `📊 **Stats for ${name}**\n\n` +
      `**Total Responses:** ${stats.totalResponses}\n` +
      `**Today:** ${stats.dailyCount}\n` +
      `**Average per day:** ${avgPerDay}\n` +
      `**First response:** ${firstDate}\n` +
      `**Last response:** ${lastDate}`;
  } else {
    // Show stats for all contacts
    let output = `📊 **Auto-Responder Statistics**\n\n`;
    
    let totalAll = 0;
    let todayAll = 0;
    
    config.watchList.forEach(contact => {
      const stats = state.stats && state.stats[contact.identifier];
      if (stats && stats.totalResponses > 0) {
        const name = contact.name || contact.identifier;
        output += `**${name}**\n`;
        output += `   Total: ${stats.totalResponses} | Today: ${stats.dailyCount}\n\n`;
        totalAll += stats.totalResponses;
        todayAll += stats.dailyCount;
      }
    });
    
    if (totalAll === 0) {
      output += `No responses sent yet.`;
    } else {
      output += `**Grand Total:** ${totalAll} responses\n`;
      output += `**Grand Today:** ${todayAll} responses`;
    }
    
    return output;
  }
}

function handleSetDailyCap(identifier, maxReplies) {
  try {
    execSync(`node "${MANAGE_SCRIPT}" set-daily-cap "${identifier}" ${maxReplies}`, { encoding: 'utf8' });
    const config = loadConfig();
    const contact = config.watchList.find(c => c.identifier === identifier);
    const name = contact ? contact.name || identifier : identifier;
    
    if (parseInt(maxReplies) === 0) {
      return `✅ Removed daily cap for ${name} (unlimited).\n\nRestart watcher to apply changes.`;
    } else {
      return `✅ Set daily cap to **${maxReplies} replies/day** for ${name}.\n\nRestart watcher to apply changes.`;
    }
  } catch (e) {
    return `❌ Failed to set daily cap:\n${e.message}`;
  }
}

// CLI interface
(async () => {
  const [,, command, ...args] = process.argv;

  try {
    let output = '';
    
    switch (command) {
      case 'list':
        output = handleList();
        break;
      
      case 'add':
        if (args.length < 3) {
          console.error('Usage: telegram-handler.js add <number> <name> <prompt>');
          process.exit(1);
        }
        output = handleAdd(args[0], args[1], args.slice(2).join(' '));
        break;
      
      case 'remove':
        if (args.length < 1) {
          console.error('Usage: telegram-handler.js remove <number>');
          process.exit(1);
        }
        output = handleRemove(args[0]);
        break;
      
      case 'edit':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js edit <number> <prompt>');
          process.exit(1);
        }
        output = handleEdit(args[0], args.slice(1).join(' '));
        break;
      
      case 'delay':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js delay <number> <minutes>');
          process.exit(1);
        }
        output = handleDelay(args[0], parseInt(args[1]));
        break;
      
      case 'toggle':
        output = handleToggle();
        break;
      
      case 'status':
        output = handleStatus();
        break;
      
      case 'history':
        if (args.length < 1) {
          console.error('Usage: telegram-handler.js history <number> [limit]');
          process.exit(1);
        }
        output = handleHistory(args[0], args[1] ? parseInt(args[1]) : 10);
        break;
      
      case 'test':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js test <number> <message>');
          process.exit(1);
        }
        output = await handleTest(args[0], args.slice(1).join(' '));
        break;
      
      case 'restart':
        output = handleRestart();
        break;
      
      case 'set-all-delays':
        if (args.length < 1) {
          console.error('Usage: telegram-handler.js set-all-delays <minutes>');
          process.exit(1);
        }
        output = handleSetAllDelays(parseInt(args[0]));
        break;
      
      case 'enable-all':
        output = handleEnableAll();
        break;
      
      case 'disable-all':
        output = handleDisableAll();
        break;
      
      case 'set-time-window':
        if (args.length < 3) {
          console.error('Usage: telegram-handler.js set-time-window <number> <start> <end>');
          process.exit(1);
        }
        output = handleSetTimeWindow(args[0], args[1], args[2]);
        break;
      
      case 'clear-time-windows':
        if (args.length < 1) {
          console.error('Usage: telegram-handler.js clear-time-windows <number>');
          process.exit(1);
        }
        output = handleClearTimeWindows(args[0]);
        break;
      
      case 'add-keyword':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js add-keyword <number> <keyword>');
          process.exit(1);
        }
        output = handleAddKeyword(args[0], args[1]);
        break;
      
      case 'remove-keyword':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js remove-keyword <number> <keyword>');
          process.exit(1);
        }
        output = handleRemoveKeyword(args[0], args[1]);
        break;
      
      case 'clear-keywords':
        if (args.length < 1) {
          console.error('Usage: telegram-handler.js clear-keywords <number>');
          process.exit(1);
        }
        output = handleClearKeywords(args[0]);
        break;
      
      case 'stats':
        output = handleStats(args[0]); // Optional contact identifier
        break;
      
      case 'set-daily-cap':
        if (args.length < 2) {
          console.error('Usage: telegram-handler.js set-daily-cap <number> <max_replies>');
          process.exit(1);
        }
        output = handleSetDailyCap(args[0], parseInt(args[1]));
        break;
      
      default:
        console.error(`Unknown command: ${command}`);
        process.exit(1);
    }
    
    console.log(output);
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
})();
