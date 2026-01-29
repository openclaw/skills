#!/usr/bin/env node

/**
 * List scheduled posts from Metricool
 */

const https = require('https');
const path = require('path');
const fs = require('fs');

const PLATFORM_NAMES = {
  'IN': 'LinkedIn',
  'TW': 'X/Twitter', 
  'BS': 'Bluesky',
  'TH': 'Threads',
  'IG': 'Instagram',
  'FB': 'Facebook',
  'TK': 'TikTok',
  'PI': 'Pinterest',
  'YT': 'YouTube'
};

function loadCredentials() {
  let token = process.env.METRICOOL_USER_TOKEN;
  let userId = process.env.METRICOOL_USER_ID;
  
  if (!token) {
    try {
      const configPath = path.join(process.env.HOME, '.moltbot', 'moltbot.json');
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      token = config.env?.vars?.METRICOOL_USER_TOKEN;
      userId = userId || config.env?.vars?.METRICOOL_USER_ID;
    } catch (e) {}
  }
  
  if (!token) {
    try {
      const envPath = path.join(__dirname, '..', '..', '..', '.env');
      const envContent = fs.readFileSync(envPath, 'utf8');
      envContent.split('\n').forEach(line => {
        const [key, ...valueParts] = line.split('=');
        const value = valueParts.join('=').trim().replace(/^["']|["']$/g, '');
        if (key === 'METRICOOL_USER_TOKEN') token = value;
        if (key === 'METRICOOL_USER_ID') userId = userId || value;
      });
    } catch (e) {}
  }
  
  return { token, userId };
}

function metricoolRequest(url, token) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'X-Mc-Auth': token,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try { resolve(JSON.parse(data)); } 
          catch { resolve(data); }
        } else {
          reject(new Error(`API error ${res.statusCode}: ${data}`));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Get first brand if no blogId specified
async function getFirstBrandId(token, userId) {
  const url = `https://app.metricool.com/api/v2/settings/brands?userId=${encodeURIComponent(userId)}&integrationSource=MCP`;
  
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: { 'X-Mc-Auth': token, 'Content-Type': 'application/json' }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          const brands = parsed.result?.data || parsed.data || parsed.result || [];
          if (brands.length > 0) {
            resolve({ id: brands[0].id, label: brands[0].label });
          } else {
            reject(new Error('No brands found'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    start: new Date().toISOString().split('T')[0],
    end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    blogId: null,
    json: false
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--start' && args[i+1]) options.start = args[++i];
    if (args[i] === '--end' && args[i+1]) options.end = args[++i];
    if (args[i] === '--blog' && args[i+1]) options.blogId = args[++i];
    if (args[i] === '--json') options.json = true;
    if (args[i] === '--help') options.help = true;
  }
  
  return options;
}

async function main() {
  const options = parseArgs();
  
  if (options.help) {
    console.log(`
List Scheduled Posts

Usage:
  node list-scheduled.js [options]

Options:
  --start DATE    Start date (default: today)
  --end DATE      End date (default: +7 days)
  --blog ID       Blog/brand ID (auto-detects first brand if not specified)
  --json          Output as JSON

Examples:
  node list-scheduled.js
  node list-scheduled.js --start 2026-01-30 --end 2026-02-05
`);
    process.exit(0);
  }
  
  const { token, userId } = loadCredentials();
  
  if (!token || !userId) {
    console.error('❌ Missing Metricool credentials');
    process.exit(1);
  }
  
  // Auto-fetch first brand if not specified
  if (!options.blogId) {
    try {
      const brand = await getFirstBrandId(token, userId);
      options.blogId = brand.id;
      if (!options.json) console.log(`📌 Using brand: ${brand.label} (${options.blogId})\n`);
    } catch (e) {
      console.error('❌ No blogId specified and could not auto-detect');
      process.exit(1);
    }
  }
  
  const timezone = encodeURIComponent('America/Chicago');
  const start = encodeURIComponent(`${options.start}T00:00:00`);
  const end = encodeURIComponent(`${options.end}T23:59:59`);
  
  const url = `https://app.metricool.com/api/v2/scheduler/posts?blogId=${options.blogId}&userId=${encodeURIComponent(userId)}&integrationSource=MCP&start=${start}&end=${end}&timezone=${timezone}&extendedRange=true`;
  
  try {
    const data = await metricoolRequest(url, token);
    const posts = data.result?.data || data.data || [];
    
    if (options.json) {
      console.log(JSON.stringify(posts, null, 2));
      return;
    }
    
    console.log(`📅 Scheduled Posts (${options.start} to ${options.end})\n`);
    
    if (posts.length === 0) {
      console.log('No scheduled posts in this range.');
      return;
    }
    
    posts.forEach((post, i) => {
      const date = new Date(post.date || post.scheduledDate);
      const dateStr = date.toLocaleDateString('en-US', { 
        weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
      });
      
      const platforms = (post.posts || [post]).map(p => 
        PLATFORM_NAMES[p.network] || p.network
      ).join(', ');
      
      const text = post.text || post.posts?.[0]?.text || '';
      const preview = text.substring(0, 50) + (text.length > 50 ? '...' : '');
      
      console.log(`${i + 1}. ${dateStr}`);
      console.log(`   📱 ${platforms}`);
      console.log(`   📝 "${preview}"`);
      if (post.id) console.log(`   🆔 ${post.id}`);
      console.log('');
    });
    
    console.log(`Total: ${posts.length} scheduled posts`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
