#!/usr/bin/env node

/**
 * iMessage Auto-Responder Watcher
 * Monitors incoming messages and auto-responds based on watch list config
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Paths
const WORKSPACE = process.env.CLAWD_WORKSPACE || path.join(os.homedir(), 'clawd');
const CONFIG_PATH = path.join(WORKSPACE, 'imsg-autoresponder.json');
const STATE_PATH = path.join(WORKSPACE, 'data', 'imsg-autoresponder-state.json');
const LOG_PATH = path.join(WORKSPACE, 'logs', 'imsg-autoresponder.log');

// Ensure directories exist
[path.dirname(STATE_PATH), path.dirname(LOG_PATH)].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Load or create config
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    const defaultConfig = {
      enabled: true,
      watchList: [],
      defaultMinMinutesBetweenReplies: 15
    };
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(defaultConfig, null, 2));
    log('Created default config at ' + CONFIG_PATH);
    return defaultConfig;
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

// Load or create state
function loadState() {
  if (!fs.existsSync(STATE_PATH)) {
    return { lastResponses: {} };
  }
  return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
}

// Save state
function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

// Log function
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());
  fs.appendFileSync(LOG_PATH, logMessage);
}

// Get message history for a chat
async function getMessageHistory(chatId, limit = 20) {
  return new Promise((resolve, reject) => {
    const proc = spawn('imsg', ['history', '--chat-id', chatId, '--limit', limit, '--json']);
    let output = '';
    let errorOutput = '';

    proc.stdout.on('data', (data) => {
      output += data.toString();
    });

    proc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`imsg history failed: ${errorOutput}`));
        return;
      }
      
      const messages = output.trim().split('\n')
        .filter(line => line)
        .map(line => JSON.parse(line));
      resolve(messages);
    });
  });
}

// Generate AI response using Anthropic API via Clawdbot config
async function generateResponse(contact, incomingMessage, messageHistory) {
  // Build conversation history for context
  const historyText = messageHistory.slice(0, 5)
    .map(m => `${m.is_from_me ? 'Me' : contact.name || contact.identifier}: ${m.text || '[attachment]'}`)
    .join('\n');

  const prompt = `${contact.prompt}

Context - Recent message history (newest first):
${historyText}

Latest message from ${contact.name || contact.identifier}:
${incomingMessage.text || '[attachment]'}

Generate a response now:`;

  // Get Anthropic API key from Clawdbot config
  const configPath = path.join(os.homedir(), '.clawdbot', 'clawdbot.json');
  let apiKey = process.env.ANTHROPIC_API_KEY;
  
  if (!apiKey && fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      apiKey = config.anthropic?.apiKey || config.providers?.anthropic?.apiKey;
    } catch (e) {
      // Ignore config parse errors
    }
  }

  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY not found. Set it in environment or ~/.clawdbot/clawdbot.json');
  }

  // Call Anthropic API
  const payload = JSON.stringify({
    model: 'claude-sonnet-4-5',
    max_tokens: 1024,
    messages: [
      { role: 'user', content: prompt }
    ]
  });

  return new Promise((resolve, reject) => {
    const proc = spawn('curl', [
      '-s',
      'https://api.anthropic.com/v1/messages',
      '-H', 'Content-Type: application/json',
      '-H', `x-api-key: ${apiKey}`,
      '-H', 'anthropic-version: 2023-06-01',
      '-d', payload
    ]);

    let output = '';
    let errorOutput = '';

    proc.stdout.on('data', (data) => {
      output += data.toString();
    });

    proc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`API call failed: ${errorOutput}`));
        return;
      }

      try {
        const response = JSON.parse(output);
        if (response.error) {
          reject(new Error(`API error: ${response.error.message}`));
          return;
        }
        
        const text = response.content[0].text;
        resolve(text);
      } catch (e) {
        reject(new Error(`Failed to parse API response: ${e.message}`));
      }
    });
  });
}

// Send message via imsg
async function sendMessage(identifier, text) {
  return new Promise((resolve, reject) => {
    const proc = spawn('imsg', ['send', '--to', identifier, '--text', text]);
    let errorOutput = '';

    proc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`imsg send failed: ${errorOutput}`));
        return;
      }
      resolve();
    });
  });
}

// Check if we should respond based on rate limiting
function shouldRespond(contact, state) {
  const now = Date.now();
  const identifier = contact.identifier;
  const minMs = (contact.minMinutesBetweenReplies || contact.defaultMinMinutesBetweenReplies || 15) * 60 * 1000;

  if (!state.lastResponses[identifier]) {
    return true;
  }

  const lastResponse = state.lastResponses[identifier];
  const elapsed = now - lastResponse;

  if (elapsed < minMs) {
    log(`Rate limit: Only ${Math.floor(elapsed / 1000 / 60)} minutes since last response to ${identifier} (need ${Math.floor(minMs / 1000 / 60)})`);
    return false;
  }

  return true;
}

// Process a new message
async function processMessage(message, config, state) {
  const contact = config.watchList.find(c => 
    c.identifier === message.identifier && c.enabled !== false
  );

  if (!contact) {
    log(`Skipping message from ${message.identifier}: not in watch list or disabled`);
    return; // Not in watch list or disabled
  }

  if (message.is_from_me) {
    return; // Don't respond to our own messages
  }

  if (!shouldRespond(contact, state)) {
    return; // Rate limited
  }

  try {
    log(`Processing message from ${contact.name || contact.identifier}: ${message.text || '[attachment]'}`);

    // Get message history for context
    const history = await getMessageHistory(message.chat_id, 20);
    
    // Generate response
    const response = await generateResponse(contact, message, history);
    log(`Generated response: ${response}`);

    // Send response
    await sendMessage(message.identifier, response);
    log(`Sent response to ${contact.name || contact.identifier}`);

    // Update state
    state.lastResponses[contact.identifier] = Date.now();
    saveState(state);

  } catch (error) {
    log(`ERROR: ${error.message}`);
  }
}

// Main watch loop
async function watch() {
  log('Starting iMessage auto-responder watcher...');
  
  const config = loadConfig();
  const state = loadState();

  if (!config.enabled) {
    log('Auto-responder is DISABLED in config. Exiting.');
    return;
  }

  if (config.watchList.length === 0) {
    log('Watch list is empty. Add contacts to the config file.');
    log(`Config: ${CONFIG_PATH}`);
    return;
  }

  log(`Watching ${config.watchList.filter(c => c.enabled !== false).length} contacts`);

  // Start watching
  const proc = spawn('imsg', ['watch', '--json']);

  proc.stdout.on('data', (data) => {
    const lines = data.toString().split('\n').filter(line => line.trim());
    
    lines.forEach(line => {
      try {
        const message = JSON.parse(line);
        log(`Received message from ${message.identifier || 'unknown'}: ${message.text || '[attachment]'} (is_from_me: ${message.is_from_me})`);
        processMessage(message, config, state);
      } catch (error) {
        log(`Failed to parse message: ${error.message}`);
      }
    });
  });

  proc.stderr.on('data', (data) => {
    log(`imsg watch error: ${data.toString()}`);
  });

  proc.on('close', (code) => {
    log(`imsg watch exited with code ${code}`);
    // Restart after a delay
    setTimeout(() => {
      log('Restarting watcher...');
      watch();
    }, 5000);
  });

  // Reload config on SIGHUP
  process.on('SIGHUP', () => {
    log('Received SIGHUP, reloading config...');
    const newConfig = loadConfig();
    Object.assign(config, newConfig);
  });
}

// Start watching
watch();
