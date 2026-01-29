#!/usr/bin/env node

/**
 * Schedule a post to Metricool
 * 
 * Usage:
 *   node schedule-post.js '{"platforms": ["linkedin", "x"], "text": "Hello world", "datetime": "2026-01-30T10:00:00"}'
 */

const https = require('https');
const path = require('path');
const fs = require('fs');

// Platform network IDs used by Metricool
const PLATFORM_IDS = {
  linkedin: 'IN',
  x: 'TW', 
  twitter: 'TW',
  bluesky: 'BS',
  threads: 'TH',
  instagram: 'IG',
  facebook: 'FB',
  tiktok: 'TK',
  pinterest: 'PI',
  youtube: 'YT'
};

// Load credentials
function loadCredentials() {
  let token = process.env.METRICOOL_USER_TOKEN;
  let userId = process.env.METRICOOL_USER_ID;
  
  // Try moltbot config
  if (!token) {
    try {
      const configPath = path.join(process.env.HOME, '.moltbot', 'moltbot.json');
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      token = config.env?.vars?.METRICOOL_USER_TOKEN;
      userId = userId || config.env?.vars?.METRICOOL_USER_ID;
    } catch (e) {}
  }
  
  // Try .env file
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

// Make API request
function metricoolRequest(endpoint, method = 'GET', body = null, token, userId) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://app.metricool.com/api/v2${endpoint}`);
    url.searchParams.set('userId', userId);
    url.searchParams.set('integrationSource', 'MCP');
    
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: method,
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
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve(data);
          }
        } else {
          reject(new Error(`Metricool API error ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
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
Metricool Post Scheduler

Usage:
  node schedule-post.js '<json-config>'

JSON Config:
  {
    "platforms": ["linkedin", "x", "bluesky", "threads", "instagram"],
    "text": "Post text" | {"linkedin": "...", "x": "..."},
    "datetime": "2026-01-30T10:00:00",
    "timezone": "America/Chicago",
    "imageUrl": "https://...",
    "blogId": "YOUR_BLOG_ID"
  }

Platforms: linkedin, x, bluesky, threads, instagram, facebook, tiktok, pinterest

Run get-brands.js to find your blog ID.

Examples:
  # Simple post to all platforms
  node schedule-post.js '{"platforms": ["linkedin", "x"], "text": "Hello!", "datetime": "2026-01-30T10:00:00"}'
  
  # Per-platform text
  node schedule-post.js '{"platforms": ["linkedin", "x"], "text": {"linkedin": "Long version...", "x": "Short"}, "datetime": "2026-01-30T10:00:00"}'
`);
    process.exit(0);
  }
  
  let config;
  try {
    config = JSON.parse(args[0]);
  } catch (e) {
    console.error('❌ Invalid JSON config');
    process.exit(1);
  }
  
  const { token, userId } = loadCredentials();
  
  if (!token || !userId) {
    console.error('❌ Missing Metricool credentials');
    console.log('Set METRICOOL_USER_TOKEN and METRICOOL_USER_ID in environment or ~/.moltbot/moltbot.json');
    process.exit(1);
  }
  
  let {
    platforms = [],
    text,
    datetime,
    timezone = 'America/Chicago',
    imageUrl,
    blogId
  } = config;
  
  // Auto-fetch first brand if not specified
  if (!blogId) {
    try {
      const brand = await getFirstBrandId(token, userId);
      blogId = brand.id;
      console.log(`📌 Using brand: ${brand.label} (${blogId})`);
    } catch (e) {
      console.error('❌ No blogId specified and could not auto-detect');
      console.log('Run get-brands.js to find your blog IDs');
      process.exit(1);
    }
  }
  
  if (!platforms.length) {
    console.error('❌ No platforms specified');
    process.exit(1);
  }
  
  if (!text) {
    console.error('❌ No text specified');
    process.exit(1);
  }
  
  if (!datetime) {
    console.error('❌ No datetime specified');
    process.exit(1);
  }
  
  // Build posts array for each platform
  const posts = platforms.map(platform => {
    const networkId = PLATFORM_IDS[platform.toLowerCase()];
    if (!networkId) {
      console.warn(`⚠️ Unknown platform: ${platform}`);
      return null;
    }
    
    // Get text for this platform
    let postText;
    if (typeof text === 'string') {
      postText = text;
    } else {
      postText = text[platform.toLowerCase()] || text.default || Object.values(text)[0];
    }
    
    const post = {
      network: networkId,
      text: postText,
      blogId: parseInt(blogId)
    };
    
    // Add media if provided
    if (imageUrl) {
      post.media = [{
        type: 'IMAGE',
        url: imageUrl
      }];
    }
    
    return post;
  }).filter(Boolean);
  
  if (posts.length === 0) {
    console.error('❌ No valid platforms');
    process.exit(1);
  }
  
  // Build schedule request
  const scheduleData = {
    blogId: parseInt(blogId),
    date: new Date(datetime).toISOString(),
    timezone: timezone,
    posts: posts
  };
  
  console.log('📤 Scheduling post...');
  console.log(`   Platforms: ${platforms.join(', ')}`);
  console.log(`   Time: ${datetime} (${timezone})`);
  if (imageUrl) console.log(`   Image: ${imageUrl}`);
  
  try {
    const result = await metricoolRequest(
      `/scheduler/posts?blogId=${blogId}`,
      'POST',
      scheduleData,
      token,
      userId
    );
    
    console.log('\n✅ Post scheduled successfully!');
    if (result.result?.id || result.id) {
      console.log(`   Post ID: ${result.result?.id || result.id}`);
    }
    console.log('\n📋 Scheduled posts preview:');
    posts.forEach(p => {
      const platName = Object.keys(PLATFORM_IDS).find(k => PLATFORM_IDS[k] === p.network);
      const preview = p.text.substring(0, 60) + (p.text.length > 60 ? '...' : '');
      console.log(`   ${platName}: "${preview}"`);
    });
    
  } catch (error) {
    console.error('\n❌ Failed to schedule:', error.message);
    
    // Provide helpful debugging info
    if (error.message.includes('401')) {
      console.log('\n💡 Check your METRICOOL_USER_TOKEN is valid');
    } else if (error.message.includes('400')) {
      console.log('\n💡 Check your post data:');
      console.log('   - Text within character limits?');
      console.log('   - Image URL publicly accessible?');
      console.log('   - Datetime in valid format?');
    }
    
    process.exit(1);
  }
}

main();
