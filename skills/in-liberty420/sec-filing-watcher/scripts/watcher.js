#!/usr/bin/env node

/**
 * SEC Filing Watcher
 * 
 * Polls SEC EDGAR RSS feeds for new filings and sends notifications
 * via webhook. Designed to work with Clawdbot but can be adapted
 * for any webhook endpoint.
 * 
 * Features:
 * - Monitors multiple tickers for specified form types
 * - Auto-seeds existing filings on first run (no spam)
 * - Auto-seeds when new tickers are added to watchlist
 * - Uses proper User-Agent to avoid SEC blocking
 * - Rate-limited to respect SEC's 10 req/sec limit
 * 
 * Usage:
 *   node watcher.js
 * 
 * Run via cron/launchd every 15 minutes for near-real-time alerts.
 */

const fs = require('fs');
const path = require('path');

// =============================================================================
// Configuration
// =============================================================================

// Skill root is parent of scripts/
const SKILL_ROOT = path.join(__dirname, '..');

const CONFIG = {
  // Paths (relative to skill root)
  watchlistPath: path.join(SKILL_ROOT, 'watchlist.json'),
  statePath: path.join(SKILL_ROOT, 'state.json'),
  
  // Webhook settings
  webhookUrl: 'http://localhost:18789/hooks/agent',
  webhookToken: '9150a681e056a67677b64dfe1c0da97d',
  
  // SEC API settings
  userAgent: 'SEC-Filing-Watcher/1.0 (contact: admin@xpindustries.xyz)',
  secBaseUrl: 'https://www.sec.gov/cgi-bin/browse-edgar',
  filingsPerRequest: 10,
  
  // Rate limiting
  delayBetweenTickers: 200,  // ms between ticker requests (SEC limit: 10/sec)
  delayBetweenNotifications: 1000,  // ms between webhook calls
  
  // Notification settings
  deliverToChannel: 'telegram',
};

// =============================================================================
// Main
// =============================================================================

async function main() {
  const watchlist = loadWatchlist();
  const { filings: seen, seededTickers, isFirstRun } = loadState();
  
  if (isFirstRun) {
    log('First run - seeding existing filings (no notifications)...');
  } else {
    log(`Checking ${watchlist.tickers.length} tickers...`);
  }
  
  let newFilingsCount = 0;
  let seededCount = 0;
  
  for (const ticker of watchlist.tickers) {
    const isNewTicker = !isFirstRun && !seededTickers.has(ticker);
    if (isNewTicker) {
      log(`  New ticker detected: ${ticker} - seeding existing filings...`);
    }
    
    try {
      const filings = await fetchFilings(ticker, watchlist.formTypes);
      
      for (const filing of filings) {
        if (seen[filing.accessionNumber]) continue;
        
        if (isFirstRun || isNewTicker) {
          log(`  SEED: ${ticker} ${filing.formType} (${filing.accessionNumber})`);
          seededCount++;
        } else {
          log(`  NEW: ${ticker} ${filing.formType} (${filing.accessionNumber})`);
          await sendNotification(ticker, filing);
          newFilingsCount++;
          await sleep(CONFIG.delayBetweenNotifications);
        }
        
        seen[filing.accessionNumber] = {
          ticker,
          formType: filing.formType,
          filedAt: filing.filedAt,
          processedAt: new Date().toISOString()
        };
      }
      
      seededTickers.add(ticker);
    } catch (err) {
      log(`  ERROR fetching ${ticker}: ${err.message}`);
    }
    
    await sleep(CONFIG.delayBetweenTickers);
  }
  
  saveState(seen, seededTickers);
  
  if (isFirstRun) {
    log(`Seeded ${seededCount} existing filing(s). Next run will notify on new filings.`);
  } else if (seededCount > 0) {
    log(`Done. Seeded ${seededCount} filing(s) for new tickers. ${newFilingsCount} new filing(s) notified.`);
  } else {
    log(`Done. ${newFilingsCount} new filing(s) found.`);
  }
}

// =============================================================================
// SEC EDGAR API
// =============================================================================

async function fetchFilings(ticker, formTypes) {
  const filings = [];
  
  for (const formType of formTypes) {
    const url = `${CONFIG.secBaseUrl}?action=getcompany&CIK=${ticker}&type=${encodeURIComponent(formType)}&dateb=&owner=include&count=${CONFIG.filingsPerRequest}&output=atom`;
    
    const res = await fetch(url, {
      headers: { 'User-Agent': CONFIG.userAgent }
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const xml = await res.text();
    const entries = parseAtomEntries(xml);
    
    for (const entry of entries) {
      filings.push({
        accessionNumber: entry.accessionNumber,
        formType: entry.formType,
        filedAt: entry.filedAt,
        title: entry.title,
        url: entry.url,
        summary: entry.summary
      });
    }
  }
  
  return filings;
}

function parseAtomEntries(xml) {
  const entries = [];
  const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
  let match;
  
  while ((match = entryRegex.exec(xml)) !== null) {
    const entryXml = match[1];
    
    // Note: SEC has a typo in their XML - "accession-nunber" instead of "accession-number"
    const accessionNumber = extractTag(entryXml, 'accession-number') || extractTag(entryXml, 'accession-nunber');
    const formType = extractTag(entryXml, 'filing-type');
    const filedAt = extractTag(entryXml, 'filing-date');
    const title = extractTag(entryXml, 'title');
    const updated = extractTag(entryXml, 'updated');
    const summary = extractTag(entryXml, 'summary');
    
    const linkMatch = entryXml.match(/<link[^>]+href="([^"]+)"/);
    const url = linkMatch ? linkMatch[1] : null;
    
    if (accessionNumber) {
      entries.push({ accessionNumber, formType, filedAt, title, url, summary, updated });
    }
  }
  
  return entries;
}

function extractTag(xml, tagName) {
  const regex = new RegExp(`<${tagName}[^>]*>([^<]*)</${tagName}>`);
  const match = xml.match(regex);
  return match ? match[1].trim() : null;
}

// =============================================================================
// Webhook Notification
// =============================================================================

async function sendNotification(ticker, filing) {
  const message = buildNotificationMessage(ticker, filing);
  
  const res = await fetch(`${CONFIG.webhookUrl}?token=${CONFIG.webhookToken}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      name: 'SEC',
      sessionKey: `hook:sec:${filing.accessionNumber}`,
      deliver: true,
      channel: CONFIG.deliverToChannel
    })
  });
  
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Webhook responded ${res.status}: ${text}`);
  }
}

function buildNotificationMessage(ticker, filing) {
  return `New SEC filing to summarize:

Ticker: ${ticker}
Form: ${filing.formType}
Filed: ${filing.filedAt}
URL: ${filing.url}

Instructions:
1. Use exec with curl to fetch the filing: curl -s -A "SEC-Filing-Watcher/1.0" "${filing.url}"
2. Analyze and summarize the key points:
   - 10-K/10-Q: earnings, guidance, risk factors
   - 8-K: material events, M&A, executive changes  
   - Form 4: insider transactions and amounts
3. Send ONE message to Telegram with:
   - Brief headline
   - Bullet-point summary of key info
   - Filing link

IMPORTANT: Do NOT narrate your process. Do NOT send multiple messages. Only send the final summary to Telegram.`;
}

// =============================================================================
// State Management
// =============================================================================

function loadWatchlist() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG.watchlistPath, 'utf8'));
  } catch (err) {
    console.error(`Error loading watchlist from ${CONFIG.watchlistPath}: ${err.message}`);
    console.error('Create a watchlist.json file with format: { "tickers": ["AAPL", "MSFT"], "formTypes": ["10-K", "10-Q", "8-K", "4"] }');
    process.exit(1);
  }
}

function loadState() {
  try {
    const data = JSON.parse(fs.readFileSync(CONFIG.statePath, 'utf8'));
    const filings = data.filings || data; // Support old format
    const seededTickers = new Set(data.seededTickers || []);
    return { filings, seededTickers, isFirstRun: false };
  } catch {
    return { filings: {}, seededTickers: new Set(), isFirstRun: true };
  }
}

function saveState(filings, seededTickers) {
  const data = {
    seededTickers: Array.from(seededTickers),
    filings
  };
  fs.writeFileSync(CONFIG.statePath, JSON.stringify(data, null, 2));
}

// =============================================================================
// Utilities
// =============================================================================

function log(message) {
  console.log(`[${new Date().toISOString()}] ${message}`);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// =============================================================================
// Entry Point
// =============================================================================

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
