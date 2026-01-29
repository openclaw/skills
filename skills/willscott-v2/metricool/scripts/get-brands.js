#!/usr/bin/env node

/**
 * List Metricool brands/accounts
 */

const https = require('https');
const path = require('path');
const fs = require('fs');

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

async function main() {
  const { token, userId } = loadCredentials();
  
  if (!token || !userId) {
    console.error('❌ Missing Metricool credentials');
    console.error('Set METRICOOL_USER_TOKEN and METRICOOL_USER_ID in environment');
    process.exit(1);
  }
  
  const url = `https://app.metricool.com/api/v2/settings/brands?userId=${encodeURIComponent(userId)}&integrationSource=MCP`;
  
  try {
    const data = await metricoolRequest(url, token);
    const brands = data.result?.data || data.data || data.result || [];
    
    if (process.argv.includes('--json')) {
      console.log(JSON.stringify(brands, null, 2));
      return;
    }
    
    console.log('\n📊 Metricool Brands\n');
    
    const brandList = Array.isArray(brands) ? brands : [brands];
    
    brandList.forEach((brand, i) => {
      console.log(`${i + 1}. ${brand.label || brand.name || brand.brandName || 'Unknown'}`);
      console.log(`   🆔 Blog ID: ${brand.id || brand.blogId}`);
      
      // List connected networks
      if (brand.networksData) {
        const networks = Object.keys(brand.networksData)
          .map(k => k.replace('Data', ''))
          .filter(n => n !== 'web')
          .map(n => n.charAt(0).toUpperCase() + n.slice(1));
        if (networks.length > 0) {
          console.log(`   📱 Networks: ${networks.join(', ')}`);
        }
      }
      console.log('');
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
