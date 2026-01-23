#!/usr/bin/env node
/**
 * Search X/Twitter using Grok's x_search tool
 * 
 * Uses xAI Responses API for real-time X search with citations
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_BASE = 'api.x.ai';
const DEFAULT_MODEL = process.env.SEARCH_X_MODEL || 'grok-4-1-fast';
const DEFAULT_DAYS = parseInt(process.env.SEARCH_X_DAYS, 10) || 30;

function getApiKey() {
  // Check environment variable
  if (process.env.XAI_API_KEY) {
    return process.env.XAI_API_KEY;
  }
  
  // Check clawdbot config (search-x skill)
  const configPath = path.join(process.env.HOME, '.clawdbot', 'clawdbot.json');
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      // Try search-x first, then xai as fallback
      const key = config?.skills?.entries?.['search-x']?.apiKey ||
                  config?.skills?.entries?.xai?.apiKey;
      if (key) return key;
    } catch (e) {}
  }
  
  return null;
}

function parseArgs(args) {
  const result = {
    query: '',
    days: DEFAULT_DAYS,
    handles: [],
    excludeHandles: [],
    json: false,
    compact: false,
    linksOnly: false,
    model: DEFAULT_MODEL,
  };
  
  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    
    if (arg === '--days' || arg === '-d') {
      result.days = parseInt(args[++i], 10);
    } else if (arg === '--handles' || arg === '-h') {
      result.handles = args[++i].split(',').map(h => h.trim().replace(/^@/, ''));
    } else if (arg === '--exclude' || arg === '-e') {
      result.excludeHandles = args[++i].split(',').map(h => h.trim().replace(/^@/, ''));
    } else if (arg === '--json' || arg === '-j') {
      result.json = true;
    } else if (arg === '--compact' || arg === '-c') {
      result.compact = true;
    } else if (arg === '--links-only' || arg === '-l') {
      result.linksOnly = true;
    } else if (arg === '--model' || arg === '-m') {
      result.model = args[++i];
    } else if (!arg.startsWith('-')) {
      result.query = args.slice(i).join(' ');
      break;
    }
    i++;
  }
  
  return result;
}

function getDateRange(days) {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - days);
  
  return {
    from_date: from.toISOString().split('T')[0],
    to_date: to.toISOString().split('T')[0],
  };
}

function extractContent(response) {
  if (!response.output) return { text: '', citations: [] };
  
  let text = '';
  let citations = [];
  
  for (const item of response.output) {
    if (item.type === 'message' && item.content) {
      for (const c of item.content) {
        if (c.type === 'output_text' && c.text) {
          text = c.text;
        }
        if (c.annotations) {
          for (const ann of c.annotations) {
            if (ann.type === 'url_citation' && ann.url) {
              if (ann.url.includes('x.com') || ann.url.includes('twitter.com')) {
                citations.push(ann.url);
              }
            }
          }
        }
      }
    }
  }
  
  // Dedupe citations
  citations = [...new Set(citations)];
  
  return { text, citations };
}

async function searchX(options) {
  const apiKey = getApiKey();
  if (!apiKey) {
    console.error('❌ No API key found.');
    console.error('   Set XAI_API_KEY or run: clawdbot config set skills.entries.search-x.apiKey "xai-YOUR-KEY"');
    console.error('   Get your key at: https://console.x.ai');
    process.exit(1);
  }
  
  const dateRange = getDateRange(options.days);
  
  // Build x_search tool config
  const xSearchTool = {
    type: 'x_search',
    x_search: {
      from_date: dateRange.from_date,
      to_date: dateRange.to_date,
    }
  };
  
  if (options.handles.length > 0) {
    xSearchTool.x_search.allowed_x_handles = options.handles;
  }
  if (options.excludeHandles.length > 0) {
    xSearchTool.x_search.excluded_x_handles = options.excludeHandles;
  }
  
  const systemPrompt = options.compact 
    ? 'You are an X/Twitter search assistant. Return only the tweets found, formatted simply with username, content, and link. No commentary.'
    : 'You are an X/Twitter search assistant. Search X and return real tweets with usernames, content, dates, and links. Be thorough but concise.';
  
  const payload = {
    model: options.model,
    input: `${systemPrompt}

Search X/Twitter for: ${options.query}

Return actual tweets with:
- @username (display name)
- Tweet content
- Date
- Link to tweet

Only include REAL posts. If none found, say so clearly.`,
    tools: [xSearchTool],
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: API_BASE,
      path: '/v1/responses',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
    }, (res) => {
      let data = '';
      
      res.on('data', chunk => data += chunk);
      
      res.on('end', () => {
        if (res.statusCode !== 200) {
          console.error(`❌ API Error (${res.statusCode}):`, data.slice(0, 500));
          process.exit(1);
        }
        
        try {
          const response = JSON.parse(data);
          
          // Full JSON output
          if (options.json) {
            console.log(JSON.stringify(response, null, 2));
            resolve(response);
            return;
          }
          
          const { text, citations } = extractContent(response);
          
          // Links only output
          if (options.linksOnly) {
            if (citations.length > 0) {
              citations.forEach(url => console.log(url));
            } else {
              console.log('No X links found.');
            }
            resolve({ text, citations });
            return;
          }
          
          // Standard or compact output
          if (text) {
            console.log(text);
          } else {
            console.log('No results found.');
          }
          
          if (!options.compact && citations.length > 0) {
            console.log('\n📎 Citations (' + citations.length + '):');
            citations.slice(0, 10).forEach(url => console.log('   ' + url));
            if (citations.length > 10) {
              console.log(`   ... and ${citations.length - 10} more`);
            }
          }
          
          resolve({ text, citations });
        } catch (e) {
          console.error('❌ Failed to parse response:', e.message);
          process.exit(1);
        }
      });
    });
    
    req.on('error', (e) => {
      console.error('❌ Request failed:', e.message);
      process.exit(1);
    });
    
    req.write(JSON.stringify(payload));
    req.end();
  });
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help')) {
  console.log(`
🔍 Search X — Real-time Twitter/X search via Grok

Usage:
  search-x [options] "your search query"

Options:
  --days, -d <n>        Search last N days (default: ${DEFAULT_DAYS})
  --handles, -h <list>  Only these handles (comma-separated, @ optional)
  --exclude, -e <list>  Exclude these handles
  --compact, -c         Minimal output (just tweets)
  --links-only, -l      Only output X links
  --json, -j            Full JSON response
  --model, -m <model>   Model (default: ${DEFAULT_MODEL})
  --help                Show this help

Examples:
  search-x "Claude Code tips"
  search-x --days 7 "AI news"
  search-x --handles elonmusk,OpenAI "AI announcements"
  search-x --days 30 --compact "Remotion video"
  search-x --links-only "trending tech"
`);
  process.exit(0);
}

const options = parseArgs(args);

if (!options.query) {
  console.error('❌ Please provide a search query');
  process.exit(1);
}

// Show search params
if (!options.json && !options.linksOnly) {
  console.error(`🔍 Searching X: "${options.query}" (last ${options.days} days)...\n`);
}

searchX(options);
