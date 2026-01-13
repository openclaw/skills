function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}

export function getConfig() {
  const baseUrl = requiredEnv('OVERSEERR_URL').replace(/\/$/, '');
  const apiKey = requiredEnv('OVERSEERR_API_KEY');
  return { baseUrl, apiKey };
}

let cachedCsrf = null;

async function getCsrfContext({ baseUrl, apiKey }) {
  if (cachedCsrf) return cachedCsrf;

  const settingsUrl = new URL(`${baseUrl}/api/v1/settings/main`);
  const settingsRes = await fetch(settingsUrl, {
    headers: { 'X-Api-Key': apiKey, Accept: 'application/json' },
  });
  const settingsText = await settingsRes.text();
  const settings = settingsText ? JSON.parse(settingsText) : {};

  const enabled = Boolean(settings?.csrfProtection);
  if (!enabled) {
    cachedCsrf = { enabled: false };
    return cachedCsrf;
  }

  const meUrl = new URL(`${baseUrl}/api/v1/auth/me`);
  const meRes = await fetch(meUrl, {
    headers: { 'X-Api-Key': apiKey, Accept: 'application/json' },
  });

  const setCookies = meRes.headers.getSetCookie ? meRes.headers.getSetCookie() : [];
  const cookieHeader = setCookies.map((c) => c.split(';')[0]).join('; ');
  const xsrfCookie = setCookies.find((c) => c.startsWith('XSRF-TOKEN='));
  const xsrfToken = xsrfCookie ? xsrfCookie.split(';')[0].slice('XSRF-TOKEN='.length) : undefined;

  cachedCsrf = { enabled: true, cookieHeader, xsrfToken };
  return cachedCsrf;
}

export async function overseerrFetch(path, { method = 'GET', query, body } = {}) {
  const { baseUrl, apiKey } = getConfig();

  const url = new URL(`${baseUrl}/api/v1${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) continue;
      url.searchParams.set(key, String(value));
    }
    // Overseerr's backend validation expects strict URL encoding; URLSearchParams encodes spaces as '+',
    // which the API rejects. Normalize '+' to '%20'.
    url.search = url.search.replace(/\+/g, '%20');
  }

  const headers = {
    'X-Api-Key': apiKey,
    Accept: 'application/json',
  };

  const isMutation = method !== 'GET' && method !== 'HEAD';
  if (isMutation) {
    const csrf = await getCsrfContext({ baseUrl, apiKey });
    if (csrf.enabled) {
      if (csrf.cookieHeader) headers.Cookie = csrf.cookieHeader;
      if (csrf.xsrfToken) {
        headers['X-CSRF-Token'] = csrf.xsrfToken;
        headers['X-XSRF-TOKEN'] = csrf.xsrfToken;
      }
    }
  }

  let payload;
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  const res = await fetch(url, {
    method,
    headers,
    body: payload,
  });

  const text = await res.text();
  let json;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { raw: text };
  }

  if (!res.ok) {
    const msg = json?.message || json?.error || `${res.status} ${res.statusText}`;
    const detail = typeof json === 'string' ? json : JSON.stringify(json);
    throw new Error(`Overseerr API error: ${msg} (${res.status})\n${detail}`);
  }

  return json;
}

export function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      args._.push(token);
      continue;
    }

    const [rawKey, inlineValue] = token.split('=', 2);
    const key = rawKey.slice(2);

    if (inlineValue !== undefined) {
      args[key] = inlineValue;
      continue;
    }

    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) {
      args[key] = true;
      continue;
    }

    args[key] = next;
    i++;
  }
  return args;
}

export function toInt(value, { name } = {}) {
  if (value === undefined || value === null) return undefined;
  const num = Number.parseInt(String(value), 10);
  if (!Number.isFinite(num)) throw new Error(`Invalid integer${name ? ` for ${name}` : ''}: ${value}`);
  return num;
}

export function parseCsvInts(value, { name } = {}) {
  if (value === undefined || value === null) return undefined;
  const str = String(value).trim();
  if (!str) return undefined;
  return str.split(',').map((v) => toInt(v.trim(), { name }));
}

export function printJson(data) {
  process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
}
