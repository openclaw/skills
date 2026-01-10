const fs = require('fs');
const path = require('path');
const os = require('os');

function getConfigPath() {
  return path.join(os.homedir(), '.homey', 'config.json');
}

/**
 * Get Homey token info from env var or config file.
 * @returns {{token: string|null, source: 'env'|'config'|null, path: string}}
 */
function getTokenInfo() {
  const configPath = getConfigPath();

  if (process.env.HOMEY_TOKEN) {
    return { token: process.env.HOMEY_TOKEN, source: 'env', path: configPath };
  }

  try {
    if (!fs.existsSync(configPath)) return { token: null, source: null, path: configPath };
    const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    return { token: cfg.token || null, source: cfg.token ? 'config' : null, path: configPath };
  } catch {
    return { token: null, source: null, path: configPath };
  }
}

/**
 * Get Homey token from env var or config file
 * @returns {string|null} Bearer token or null
 */
function getToken() {
  return getTokenInfo().token;
}

/**
 * Save token to config file (~/.homey/config.json)
 * @param {string} token Bearer token
 */
function saveToken(token) {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);

  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  fs.writeFileSync(configPath, JSON.stringify({ token }, null, 2) + '\n', {
    encoding: 'utf8',
    mode: 0o600,
  });

  // Best-effort: enforce private permissions even if file already existed.
  try {
    fs.chmodSync(configPath, 0o600);
  } catch {
    // ignore
  }
}

module.exports = {
  getTokenInfo,
  getToken,
  saveToken,
};
