#!/usr/bin/env node

/**
 * iMessage Auto-Responder Watcher (Polling Version)
 * Polls for new messages instead of using `imsg watch`
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

// Poll interval (milliseconds)
const POLL_INTERVAL = 5000; // 5 seconds

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
    return { 
      lastResponses: {}, 
      lastChecked: {}, 
      processing: {},
      stats: {}
    };
  }
  const state = JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
  // Ensure required fields exist
  if (!state.processing) {
    state.processing = {};
  }
  if (!state.stats) {
    state.stats = {};
  }
  return state;
}

// Save state
function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

// Log function
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  // Only append to file, don't console.log (launcher already redirects stdout)
  fs.appendFileSync(LOG_PATH, logMessage);
}

// Get chat list
async function getChatList() {
  return new Promise((resolve, reject) => {
    const proc = spawn('imsg', ['chats', '--limit', '50', '--json']);
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
        reject(new Error(`imsg chats failed: ${errorOutput}`));
        return;
      }
      
      const chats = output.trim().split('\n')
        .filter(line => line)
        .map(line => JSON.parse(line));
      resolve(chats);
    });
  });
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

// Generate AI response using OpenAI API
async function generateResponse(contact, incomingMessage, messageHistory) {
  const historyText = messageHistory.slice(0, 5)
    .map(m => `${m.is_from_me ? 'Me' : contact.name || contact.identifier}: ${m.text || '[attachment]'}`)
    .join('\n');

  const prompt = `${contact.prompt}

Context - Recent message history (newest first):
${historyText}

Latest message from ${contact.name || contact.identifier}:
${incomingMessage.text || '[attachment]'}

Generate a response now:`;

  // Get OpenAI API key from Clawdbot config
  const configPath = path.join(os.homedir(), '.clawdbot', 'clawdbot.json');
  let apiKey = process.env.OPENAI_API_KEY;
  
  if (!apiKey && fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      apiKey = config.skills?.['openai-whisper-api']?.apiKey || config.skills?.['openai-image-gen']?.apiKey;
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
// Check if current time is within allowed time windows
function isWithinTimeWindow(contact) {
  // If no time windows configured, always allow
  if (!contact.timeWindows || contact.timeWindows.length === 0) {
    return true;
  }

  const now = new Date();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();
  const currentTime = currentHour * 60 + currentMinute; // minutes since midnight

  // Check each time window
  for (const window of contact.timeWindows) {
    const [startHour, startMinute] = window.start.split(':').map(Number);
    const [endHour, endMinute] = window.end.split(':').map(Number);
    
    const startTime = startHour * 60 + startMinute;
    const endTime = endHour * 60 + endMinute;

    if (currentTime >= startTime && currentTime <= endTime) {
      return true; // Within an allowed window
    }
  }

  return false; // Outside all windows
}

// Check if message contains required keywords
function messageMatchesKeywords(contact, messageText) {
  // If no keywords configured, always allow
  if (!contact.keywords || contact.keywords.length === 0) {
    return true;
  }

  // Check if message contains any of the keywords (case-insensitive)
  const lowerText = (messageText || '').toLowerCase();
  
  for (const keyword of contact.keywords) {
    if (lowerText.includes(keyword.toLowerCase())) {
      return true; // Found a matching keyword
    }
  }

  return false; // No keywords matched
}

function shouldRespond(contact, state, config, messageText) {
  const now = Date.now();
  const identifier = contact.identifier;
  const minMs = (contact.minMinutesBetweenReplies !== undefined ? contact.minMinutesBetweenReplies : config.defaultMinMinutesBetweenReplies) * 60 * 1000;

  // Check time windows first
  if (!isWithinTimeWindow(contact)) {
    log(`Time window: Outside allowed hours for ${contact.name || identifier}`);
    return false;
  }

  // Check keyword triggers
  if (!messageMatchesKeywords(contact, messageText)) {
    log(`Keyword filter: Message doesn't contain required keywords for ${contact.name || identifier}`);
    return false;
  }

  // Check daily reply cap
  if (contact.maxRepliesPerDay && contact.maxRepliesPerDay > 0) {
    const stats = state.stats && state.stats[identifier];
    if (stats) {
      const today = new Date().toDateString();
      // Reset daily count if new day
      if (stats.dailyDate !== today) {
        stats.dailyCount = 0;
        stats.dailyDate = today;
      }
      
      if (stats.dailyCount >= contact.maxRepliesPerDay) {
        log(`Daily cap: Already sent ${stats.dailyCount} responses today for ${contact.name || identifier} (max: ${contact.maxRepliesPerDay})`);
        return false;
      }
    }
  }

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

// Check for new messages and respond
async function checkForNewMessages(config, state) {
  try {
    const chats = await getChatList();
    
    for (const chat of chats) {
      const contact = config.watchList.find(c => c.identifier === chat.identifier && c.enabled !== false);
      
      if (!contact) {
        continue; // Not in watch list
      }

      // Get recent messages
      const messages = await getMessageHistory(chat.id, 5);
      
      if (messages.length === 0) {
        continue;
      }

      // Get the most recent message
      const latestMessage = messages[0];
      
      // Skip if it's from us
      if (latestMessage.is_from_me) {
        continue;
      }

      // Check if we've already seen this message
      const lastCheckedTime = state.lastChecked[contact.identifier] || 0;
      const messageTime = new Date(latestMessage.created_at).getTime();
      
      if (messageTime <= lastCheckedTime) {
        continue; // Already seen this message
      }

      // Check if currently processing this contact (prevent race condition)
      if (state.processing[contact.identifier]) {
        log(`Skipping ${contact.name || contact.identifier} - already processing`);
        continue;
      }

      // Update last checked time and mark as processing
      state.lastChecked[contact.identifier] = messageTime;
      state.processing[contact.identifier] = true;
      saveState(state);

      log(`New message from ${contact.name || contact.identifier}: ${latestMessage.text || '[attachment]'}`);

      // Check rate limiting and conditions
      if (!shouldRespond(contact, state, config, latestMessage.text)) {
        state.processing[contact.identifier] = false;
        saveState(state);
        continue;
      }

      // Generate and send response
      try {
        log(`Generating response for ${contact.name || contact.identifier}...`);
        const response = await generateResponse(contact, latestMessage, messages);
        log(`Generated response: ${response}`);

        await sendMessage(contact.identifier, response);
        log(`✓ Sent response to ${contact.name || contact.identifier}`);

        // Update state
        state.lastResponses[contact.identifier] = Date.now();
        state.processing[contact.identifier] = false;
        
        // Update statistics
        if (!state.stats[contact.identifier]) {
          state.stats[contact.identifier] = {
            totalResponses: 0,
            firstResponse: Date.now(),
            lastResponse: Date.now(),
            dailyCount: 0,
            dailyDate: new Date().toDateString()
          };
        }
        
        const stats = state.stats[contact.identifier];
        const today = new Date().toDateString();
        
        // Reset daily count if it's a new day
        if (stats.dailyDate !== today) {
          stats.dailyCount = 0;
          stats.dailyDate = today;
        }
        
        stats.totalResponses++;
        stats.dailyCount++;
        stats.lastResponse = Date.now();
        
        saveState(state);

      } catch (error) {
        log(`ERROR generating/sending response: ${error.message}`);
        state.processing[contact.identifier] = false;
        saveState(state);
      }
    }

  } catch (error) {
    log(`ERROR checking messages: ${error.message}`);
  }
}

// Main polling loop
async function startPolling() {
  log('Starting iMessage auto-responder (polling mode)...');
  
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

  log(`Watching ${config.watchList.filter(c => c.enabled !== false).length} contacts (polling every ${POLL_INTERVAL/1000}s)`);

  // Clear all processing locks on startup (prevent stuck contacts from previous crashes)
  const stuckContacts = Object.keys(state.processing).filter(id => state.processing[id]);
  if (stuckContacts.length > 0) {
    log(`Clearing ${stuckContacts.length} stale processing locks from previous session`);
    state.processing = {};
  }

  // Initialize lastChecked for all contacts if not present
  config.watchList.forEach(contact => {
    if (!state.lastChecked[contact.identifier]) {
      state.lastChecked[contact.identifier] = Date.now();
    }
  });
  saveState(state);

  // Poll continuously
  setInterval(async () => {
    await checkForNewMessages(config, state);
  }, POLL_INTERVAL);

  // Also check immediately
  await checkForNewMessages(config, state);
}

// Start
startPolling();
