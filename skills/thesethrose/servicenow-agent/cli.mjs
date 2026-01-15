#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadDotEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const text = fs.readFileSync(filePath, 'utf8');
  const env = {};
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('-')) {
      args._.push(token);
      continue;
    }
    if (token === '--') {
      args._.push(...argv.slice(i + 1));
      break;
    }
    const next = argv[i + 1];
    if (token.includes('=')) {
      const [key, value] = token.split('=');
      args[key.replace(/^--/, '')] = value;
    } else if (next && !next.startsWith('-')) {
      args[token.replace(/^--/, '')] = next;
      i += 1;
    } else {
      args[token.replace(/^--/, '')] = true;
    }
  }
  return args;
}

function buildBaseUrl(domain) {
  if (!domain) return '';
  if (domain.startsWith('http://') || domain.startsWith('https://')) return domain.replace(/\/$/, '');
  return `https://${domain.replace(/\/$/, '')}`;
}

function buildQuery(params) {
  const query = new URLSearchParams();
  const allowed = [
    'sysparm_query',
    'sysparm_display_value',
    'sysparm_exclude_reference_link',
    'sysparm_suppress_pagination_header',
    'sysparm_fields',
    'sysparm_limit',
    'sysparm_view',
    'sysparm_query_category',
    'sysparm_query_no_domain',
    'sysparm_no_count',
  ];
  for (const key of allowed) {
    if (params[key] !== undefined) {
      query.set(key, String(params[key]));
    }
  }
  return query.toString();
}

function resolveAuth(args, dotenv) {
  const domain = args.domain || process.env.SERVICENOW_DOMAIN || dotenv.SERVICENOW_DOMAIN;
  const username = args.username || args.user || process.env.SERVICENOW_USERNAME || dotenv.SERVICENOW_USERNAME;
  const password = args.password || args.pass || process.env.SERVICENOW_PASSWORD || dotenv.SERVICENOW_PASSWORD;
  return { domain, username, password };
}

function formatHelp() {
  return `ServiceNow Table API CLI (read-only)

Usage:
  cli.mjs list <table> [options]
  cli.mjs get <table> <sys_id> [options]
  cli.mjs batch <file.json> [options]

Auth (flags override env):
  --domain <domain>     ServiceNow instance domain
  --username <user>     Basic auth username (alias: --user)
  --password <pass>     Basic auth password (alias: --pass)

Common options:
  --sysparm_query <q>
  --sysparm_fields <fields>
  --sysparm_limit <n>
  --sysparm_display_value <true|false|all>
  --sysparm_exclude_reference_link <true|false>
  --pretty              Pretty-print JSON

Examples:
  node cli.mjs list incident --sysparm_limit 5 --sysparm_fields number,short_description
  node cli.mjs get incident <sys_id> --sysparm_fields number,opened_at
  node cli.mjs batch specialists/incidents.json
`;
}

async function requestJson(baseUrl, username, password, pathAndQuery) {
  const auth = Buffer.from(`${username}:${password}`).toString('base64');
  const url = `${baseUrl}${pathAndQuery}`;
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Authorization': `Basic ${auth}`,
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 500)}`);
  }
  return text;
}

async function handleList(args, auth, pretty) {
  const table = args._[1];
  if (!table) throw new Error('Missing <table>');
  const query = buildQuery(args);
  const pathAndQuery = query
    ? `/api/now/table/${encodeURIComponent(table)}?${query}`
    : `/api/now/table/${encodeURIComponent(table)}`;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function handleGet(args, auth, pretty) {
  const table = args._[1];
  const sysId = args._[2];
  if (!table || !sysId) throw new Error('Missing <table> or <sys_id>');
  const query = buildQuery(args);
  const pathAndQuery = query
    ? `/api/now/table/${encodeURIComponent(table)}/${encodeURIComponent(sysId)}?${query}`
    : `/api/now/table/${encodeURIComponent(table)}/${encodeURIComponent(sysId)}`;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function handleBatch(args, auth, pretty) {
  const filePath = args._[1];
  if (!filePath) throw new Error('Missing <file.json>');
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
  const text = fs.readFileSync(absolutePath, 'utf8');
  const data = JSON.parse(text);
  const requests = Array.isArray(data) ? data : data.requests;
  if (!Array.isArray(requests)) {
    throw new Error('Batch file must be an array or { "requests": [...] }');
  }

  const results = [];
  for (const req of requests) {
    const table = req.table;
    if (!table) {
      results.push({ name: req.name || null, error: 'Missing table' });
      continue;
    }
    const params = { ...req };
    delete params.name;
    delete params.table;
    delete params.sys_id;
    const query = buildQuery(params);

    let pathAndQuery = `/api/now/table/${encodeURIComponent(table)}`;
    if (req.sys_id) {
      pathAndQuery += `/${encodeURIComponent(req.sys_id)}`;
    }
    if (query) {
      pathAndQuery += `?${query}`;
    }

    try {
      const body = await requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery);
      results.push({ name: req.name || null, ok: true, result: JSON.parse(body) });
    } catch (error) {
      results.push({ name: req.name || null, ok: false, error: String(error) });
    }
  }

  return JSON.stringify(results, null, pretty ? 2 : 0);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] || 'help';
  if (args.help || command === 'help' || command === '--help' || command === '-h') {
    console.log(formatHelp());
    return;
  }

  const dotenv = loadDotEnv(path.join(__dirname, '.env'));
  const { domain, username, password } = resolveAuth(args, dotenv);
  const baseUrl = buildBaseUrl(domain);

  if (!baseUrl || !username || !password) {
    throw new Error('Missing auth. Set SERVICENOW_DOMAIN, SERVICENOW_USERNAME, SERVICENOW_PASSWORD or pass --domain/--username/--password.');
  }

  const auth = { baseUrl, username, password };
  const pretty = Boolean(args.pretty);
  let text;

  if (command === 'list') {
    text = await handleList(args, auth, pretty);
  } else if (command === 'get') {
    text = await handleGet(args, auth, pretty);
  } else if (command === 'batch') {
    text = await handleBatch(args, auth, pretty);
  } else {
    throw new Error(`Unknown command: ${command}`);
  }

  if (command === 'batch') {
    console.log(text);
    return;
  }

  if (pretty) {
    try {
      console.log(JSON.stringify(JSON.parse(text), null, 2));
      return;
    } catch {
      console.log(text);
      return;
    }
  }

  console.log(text);
}

main().catch((error) => {
  console.error(`Error: ${error.message || error}`);
  process.exit(1);
});