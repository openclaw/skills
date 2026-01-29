#!/usr/bin/env node

/**
 * Get best time to post for a platform
 */

const https = require('https');
const path = require('path');
const fs = require('fs');

const PLATFORM_IDS = {
  linkedin: 'IN',
  x: 'TW', 
  twitter: 'TW',
  bluesky: 'BS',
  threads: 'TH',
  instagram: 'IG',
  facebook: 'FB'
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

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
Get Best Time to Post

Usage:
  node best-time.js <platform> [--blog <id>]

Platforms: linkedin, x, bluesky, threads, instagram, facebook

Examples:
  node best-time.js linkedin
  node best-time.js x --blog 12345
`);
    process.exit(0);
  }
  
  const platform = args[0].toLowerCase();
  const networkId = PLATFORM_IDS[platform];
  
  if (!networkId) {
    console.error(`❌ Unknown platform: ${platform}`);
    console.log('Valid platforms:', Object.keys(PLATFORM_IDS).join(', '));
    process.exit(1);
  }
  
  const { token, userId } = loadCredentials();
  
  if (!token || !userId) {
    console.error('❌ Missing Metricool credentials');
    process.exit(1);
  }
  
  const blogIndex = args.indexOf('--blog');
  let blogId = blogIndex > -1 ? args[blogIndex + 1] : null;
  
  // Auto-fetch first brand if not specified
  if (!blogId) {
    try {
      const brand = await getFirstBrandId(token, userId);
      blogId = brand.id;
      console.log(`📌 Using brand: ${brand.label} (${blogId})\n`);
    } catch (e) {
      console.error('❌ No blogId specified and could not auto-detect');
      process.exit(1);
    }
  }
  
  const url = `https://app.metricool.com/api/v2/analytics/best-time?blogId=${blogId}&userId=${encodeURIComponent(userId)}&integrationSource=MCP&network=${networkId}`;
  
  try {
    const data = await metricoolRequest(url, token);
    const result = data.result?.data || data.data || data.result || data;
    
    if (process.argv.includes('--json')) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    
    console.log(`⏰ Best Time to Post on ${platform.charAt(0).toUpperCase() + platform.slice(1)}\n`);
    
    // Parse and display best times
    if (result.days || result.hours) {
      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      
      if (result.bestTimes) {
        console.log('Top recommended times:');
        result.bestTimes.slice(0, 5).forEach((t, i) => {
          console.log(`  ${i + 1}. ${days[t.day]} at ${t.hour}:00 (score: ${t.value})`);
        });
      } else {
        console.log(JSON.stringify(result, null, 2));
      }
    } else {
      console.log(JSON.stringify(result, null, 2));
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
