#!/usr/bin/env node
/**
 * Antigravity Quota Checker
 * 
 * Check quota status for all Antigravity accounts configured in Clawdbot.
 * 
 * Usage: 
 *   node check-quota.js [options]
 * 
 * Options:
 *   --table      Output markdown table (pipe to tablesnap for image)
 *   --json       Output JSON
 *   --tz ZONE    Timezone for reset times (default: local or TZ env)
 * 
 * Examples:
 *   node check-quota.js
 *   node check-quota.js --table | tablesnap --theme light -o quota.png
 *   node check-quota.js --json
 *   TZ=America/New_York node check-quota.js
 * 
 * Quota Info:
 *   - Each model type (Claude, Gemini Pro, Gemini Flash) has its own 5-hour reset window
 *   - Quotas are per-account
 * 
 * Requires:
 *   - Clawdbot with Antigravity accounts configured
 *   - Auth profiles at ~/.clawdbot/agents/main/agent/auth-profiles.json
 *     or ~/.clawdbot/agent/auth-profiles.json
 */

const fs = require('fs');
const path = require('path');

// OAuth credentials (Antigravity public client)
const CLIENT_ID = Buffer.from("MTA3MTAwNjA2MDU5MS10bWhzc2luMmgyMWxjcmUyMzV2dG9sb2poNGc0MDNlcC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbQ==", 'base64').toString();
const CLIENT_SECRET = Buffer.from("R09DU1BYLUs1OEZXUjQ4NkxkTEoxbUxCOHNYQzR6NnFEQWY=", 'base64').toString();
const TOKEN_URL = "https://oauth2.googleapis.com/token";
const ENDPOINT = "https://cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels";

// Parse args
const args = process.argv.slice(2);
const tableMode = args.includes('--table');
const jsonMode = args.includes('--json');
const tzIndex = args.indexOf('--tz');
const timezone = tzIndex !== -1 ? args[tzIndex + 1] : (process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone);

// Models to check
const TARGET_MODELS = [
  'claude-opus-4-5-thinking',
  'claude-sonnet-4-5-thinking', 
  'claude-sonnet-4-5',
  'gemini-3-flash',
  'gemini-3-pro-high',
];

async function refreshToken(refreshTokenValue) {
  const response = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: refreshTokenValue,
      grant_type: 'refresh_token',
    }),
  });
  
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Token refresh failed: ${response.status}`);
  }
  
  const data = await response.json();
  return data.access_token;
}

async function fetchQuota(accessToken, projectId) {
  const response = await fetch(ENDPOINT, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      'User-Agent': 'antigravity/0.2.0',
    },
    body: JSON.stringify({ project: projectId }),
  });
  
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Quota fetch failed: ${response.status}`);
  }
  
  return response.json();
}

function formatTime(isoString) {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    const now = new Date();
    const hoursUntilReset = (date - now) / (1000 * 60 * 60);
    
    // If reset is more than 8 hours away, include the date
    if (hoursUntilReset > 8) {
      return date.toLocaleDateString('en-US', {
        timeZone: timezone,
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    }
    
    return date.toLocaleTimeString('en-US', { 
      timeZone: timezone, 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  } catch {
    return new Date(isoString).toLocaleTimeString();
  }
}

function formatQuota(models) {
  const results = [];
  
  for (const modelId of TARGET_MODELS) {
    const model = models[modelId];
    if (model?.quotaInfo) {
      // If remainingFraction is missing/null, quota is exhausted (0%)
      const fraction = model.quotaInfo.remainingFraction ?? 0;
      const pct = (fraction * 100).toFixed(1);
      results.push({ 
        model: modelId, 
        quota: parseFloat(pct), 
        quotaStr: `${pct}%`, 
        reset: formatTime(model.quotaInfo.resetTime),
        resetTime: model.quotaInfo.resetTime 
      });
    }
  }
  
  return results;
}

function getQuotaEmoji(pct) {
  if (pct >= 80) return '🟢';
  if (pct >= 50) return '🟡';
  if (pct >= 20) return '🟠';
  return '🔴';
}

function findAuthProfiles() {
  const possiblePaths = [
    path.join(process.env.HOME, '.clawdbot/agents/main/agent/auth-profiles.json'),
    path.join(process.env.HOME, '.clawdbot/agent/auth-profiles.json'),
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  
  return null;
}

async function main() {
  // Find auth profiles
  const profilesPath = findAuthProfiles();
  
  if (!profilesPath) {
    console.error('❌ No Antigravity auth profiles found.');
    console.error('   Expected at: ~/.clawdbot/agents/main/agent/auth-profiles.json');
    console.error('   Run `clawdbot configure` to add accounts.');
    process.exit(1);
  }
  
  let profiles;
  try {
    profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf-8'));
  } catch (err) {
    console.error(`❌ Failed to read auth profiles: ${err.message}`);
    process.exit(1);
  }
  
  const accounts = Object.entries(profiles.profiles || {})
    .filter(([key]) => key.startsWith('google-antigravity:'))
    .map(([key, value]) => ({
      email: key.replace('google-antigravity:', ''),
      refresh: value.refresh,
      projectId: value.projectId,
    }));
  
  if (accounts.length === 0) {
    console.error('❌ No Antigravity accounts found in auth profiles.');
    console.error('   Run `clawdbot configure` to add accounts.');
    process.exit(1);
  }
  
  if (!tableMode && !jsonMode) {
    console.log(`\n📊 Antigravity Quota Check - ${new Date().toISOString()}`);
    console.log(`⏰ Each model type resets every 5 hours (Claude, Gemini Pro, Flash have separate quotas)`);
    console.log(`🌍 Times shown in: ${timezone}\n`);
    console.log(`Found ${accounts.length} account(s)\n`);
  }
  
  const allResults = [];
  
  for (const account of accounts) {
    if (!tableMode && !jsonMode) {
      console.log(`🔍 ${account.email} (${account.projectId})`);
    }
    
    try {
      const accessToken = await refreshToken(account.refresh);
      const data = await fetchQuota(accessToken, account.projectId);
      
      if (data.models) {
        const quotas = formatQuota(data.models);
        
        if (quotas.length > 0) {
          if (!tableMode && !jsonMode) {
            for (const q of quotas) {
              console.log(`   ${q.model}: ${q.quotaStr} (resets ${q.reset})`);
            }
          }
          allResults.push({ email: account.email, projectId: account.projectId, quotas });
        } else {
          if (!tableMode && !jsonMode) console.log(`   No quota info available`);
        }
      } else {
        if (!tableMode && !jsonMode) console.log(`   No models returned`);
      }
    } catch (err) {
      if (!tableMode && !jsonMode) console.log(`   ❌ Error: ${err.message}`);
      allResults.push({ email: account.email, error: err.message });
    }
    
    if (!tableMode && !jsonMode) console.log('');
  }
  
  // Sort by Opus quota descending
  const sortedResults = allResults
    .filter(r => !r.error)
    .map(r => {
      const opus = r.quotas.find(q => q.model === 'claude-opus-4-5-thinking');
      return { email: r.email, projectId: r.projectId, opus, quotas: r.quotas };
    })
    .filter(r => r.opus)
    .sort((a, b) => b.opus.quota - a.opus.quota);
  
  if (jsonMode) {
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      timezone,
      accounts: sortedResults.map(r => ({
        email: r.email,
        projectId: r.projectId,
        quotas: Object.fromEntries(r.quotas.map(q => [q.model, { remaining: q.quota, reset: q.resetTime }]))
      }))
    }, null, 2));
  } else if (tableMode) {
    // Markdown table for tablesnap
    console.log('| Account | Claude | Reset | Gemini Pro | Reset | Flash | Reset |');
    console.log('|---------|--------|-------|------------|-------|-------|-------|');
    
    for (const r of sortedResults) {
      const shortEmail = r.email.split('@')[0];
      const opus = r.quotas.find(q => q.model === 'claude-opus-4-5-thinking');
      const pro = r.quotas.find(q => q.model === 'gemini-3-pro-high');
      const flash = r.quotas.find(q => q.model === 'gemini-3-flash');
      
      const opusStr = opus ? `${getQuotaEmoji(opus.quota)} ${opus.quotaStr}` : 'N/A';
      const opusReset = opus ? opus.reset : '-';
      const proStr = pro ? `${getQuotaEmoji(pro.quota)} ${pro.quotaStr}` : 'N/A';
      const proReset = pro ? pro.reset : '-';
      const flashStr = flash ? `${getQuotaEmoji(flash.quota)} ${flash.quotaStr}` : 'N/A';
      const flashReset = flash ? flash.reset : '-';
      
      console.log(`| ${shortEmail} | ${opusStr} | ${opusReset} | ${proStr} | ${proReset} | ${flashStr} | ${flashReset} |`);
    }
  } else {
    // Text summary
    console.log('─'.repeat(60));
    console.log('Summary (Claude Opus quota, sorted by remaining):');
    for (const r of sortedResults) {
      const emoji = getQuotaEmoji(r.opus.quota);
      console.log(`  ${emoji} ${r.email}: ${r.opus.quotaStr} (resets ${r.opus.reset})`);
    }
  }
}

main().catch(err => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
