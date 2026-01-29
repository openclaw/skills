#!/usr/bin/env node
// Minimal AFKL Open Data HTTP helper.
import fs from 'node:fs';
import path from 'node:path';

export function getStateDir() {
  // Prefer explicit env.
  if (process.env.CLAWDBOT_STATE_DIR) return process.env.CLAWDBOT_STATE_DIR;
  if (process.env.AFKL_STATE_DIR) return process.env.AFKL_STATE_DIR;

  // Clawdbot default workspace state dir (when running on the Snowi host).
  const defaultDir = '/home/cwehrung/clawd/state';
  try {
    if (fs.existsSync(defaultDir)) return defaultDir;
  } catch {}

  // Fallback for community usage.
  return path.resolve(process.cwd(), 'state');
}

export function loadCreds() {
  // Prefer env vars for community/shared skill usage.
  const apiKeyEnv = (process.env.AFKL_API_KEY || '').trim();
  const apiSecretEnv = (process.env.AFKL_API_SECRET || '').trim();

  const stateDir = getStateDir();
  const apiKeyPath = path.join(stateDir, 'afkl_api_key.txt');
  const apiSecretPath = path.join(stateDir, 'afkl_api_secret.txt');

  const apiKey = apiKeyEnv || (fs.existsSync(apiKeyPath) ? fs.readFileSync(apiKeyPath, 'utf8').trim() : '');
  const apiSecret = apiSecretEnv || (fs.existsSync(apiSecretPath) ? fs.readFileSync(apiSecretPath, 'utf8').trim() : '');
  return { apiKey, apiSecret };
}

export async function afklFetchJson(url, { accept = '*/*' } = {}) {
  const { apiKey, apiSecret } = loadCreds();
  if (!apiKey) throw new Error('Missing AFKL API key (state/afkl_api_key.txt)');

  const headers = {
    // The gateway is picky: Accept */* yields application/hal+json reliably.
    'Accept': accept,
    'API-Key': apiKey,
  };
  if (apiSecret) headers['API-Secret'] = apiSecret;

  const resp = await fetch(url, { headers });
  const text = await resp.text();
  let json = null;
  try { json = JSON.parse(text); } catch {}
  if (!resp.ok) {
    const err = new Error(`AFKL HTTP ${resp.status}`);
    err.status = resp.status;
    err.body = json || text.slice(0, 400);
    err.url = url;
    throw err;
  }
  return json;
}
