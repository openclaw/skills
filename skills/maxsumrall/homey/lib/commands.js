const chalk = require('chalk');
const Table = require('cli-table3');
const HomeyClient = require('./client');
const config = require('./config');
const { discoverLocalHomeys, formatCandidates, requireDiscovered } = require('./discover-local');

/**
 * Create Homey client from config
 */
const { cliError } = require('./errors');

function createClient() {
  const conn = config.getConnectionInfo();

  if (conn.modeSelected === 'local') {
    const missing = [];
    if (!conn.local.address) missing.push('HOMEY_ADDRESS');
    if (!conn.local.token) missing.push('HOMEY_LOCAL_TOKEN');

    if (missing.length) {
      throw cliError(
        'NO_TOKEN',
        'local mode selected but local Homey address/token are not configured',
        {
          modeWanted: conn.modeWanted,
          modeSelected: conn.modeSelected,
          missing,
          path: conn.path,
          help:
            'Local mode (LAN/VPN):\n' +
            '  1) Generate a local API key in the Homey Web App\n' +
            '  2) Configure address + token:\n' +
            '     export HOMEY_MODE=local\n' +
            '     homeycli auth discover-local --save\n' +
            '     echo "<LOCAL_API_KEY>" | homeycli auth set-local --stdin\n' +
            '     # (or set address explicitly: --address http://<homey-ip>)\n\n' +
            'Cloud mode (remote/headless):\n' +
            '  1) Create a token in Homey Developer Tools\n' +
            '  2) Configure token:\n' +
            '     export HOMEY_MODE=cloud\n' +
            '     echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin\n\n' +
            'OAuth (advanced): https://api.developer.homey.app/',
        }
      );
    }

    return new HomeyClient({
      mode: 'local',
      address: conn.local.address,
      token: conn.local.token,
    });
  }

  // Cloud mode
  if (!conn.cloud.token) {
    throw cliError(
      'NO_TOKEN',
      'cloud mode selected but no cloud token is configured',
      {
        modeWanted: conn.modeWanted,
        modeSelected: conn.modeSelected,
        missing: ['HOMEY_TOKEN'],
        path: conn.path,
        help:
          'Cloud mode (remote/headless):\n' +
          '  1) Create a token in Homey Developer Tools\n' +
          '  2) Configure token:\n' +
          '     export HOMEY_MODE=cloud\n' +
          '     echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin\n\n' +
          'Local mode (LAN/VPN):\n' +
          '  export HOMEY_MODE=local\n' +
          '  homeycli auth discover-local --save\n' +
          '  echo "<LOCAL_API_KEY>" | homeycli auth set-local --stdin\n\n' +
          'OAuth (advanced): https://api.developer.homey.app/',
      }
    );
  }

  return new HomeyClient({ mode: 'cloud', token: conn.cloud.token });
}

/**
 * Output data as JSON or pretty table
 */
function output(data, options = {}) {
  if (options.json) {
    console.log(JSON.stringify(data, null, 2));
  } else if (options.formatter) {
    options.formatter(data);
  } else {
    console.log(data);
  }
}

function parseBoolean(value) {
  const v = String(value).toLowerCase();
  if (['true', '1', 'on', 'yes', 'y'].includes(v)) return true;
  if (['false', '0', 'off', 'no', 'n'].includes(v)) return false;
  return null;
}

/**
 * List all devices
 */
async function listDevices(options) {
  const client = createClient();
  const devices = options.match
    ? await client.searchDevices(options.match, options)
    : await client.getDevices(options);

  if (options.json) {
    output(devices, options);
    return;
  }

  const table = new Table({
    head: [
      chalk.cyan('Name'),
      chalk.cyan('Zone'),
      chalk.cyan('Class'),
      chalk.cyan('Capabilities'),
      chalk.cyan('State'),
    ],
    colWidths: [25, 20, 15, 30, 15],
  });

  for (const device of devices) {
    const caps = (device.capabilities || []).slice(0, 3).join(', ');
    const capsDisplay = (device.capabilities || []).length > 3
      ? `${caps}... (+${device.capabilities.length - 3})`
      : caps;

    const state = device.available
      ? chalk.green('✓ Available')
      : chalk.red('✗ Unavailable');

    table.push([
      device.name,
      device.zoneName || device.zoneId || device.zone || '-',
      device.class,
      capsDisplay,
      state,
    ]);
  }

  console.log(chalk.bold(`\n📱 Found ${devices.length} devices:\n`));
  console.log(table.toString());
}

/**
 * Control a device (on/off)
 */
async function controlDevice(name, action, options) {
  const client = createClient();
  const device = await client.getDevice(name, options);

  if (!(device.capabilities || []).includes('onoff')) {
    throw cliError('CAPABILITY_NOT_SUPPORTED', `device '${device.name}' does not support on/off`, {
      device: { id: device.id, name: device.name },
      capability: 'onoff',
      available: device.capabilities || [],
    });
  }

  const value = action === 'on';
  await client.setCapability(device.id, 'onoff', value);

  if (!options.json) {
    console.log(chalk.green(`✓ Turned ${device.name} ${action}`));
  } else {
    output({ success: true, device: device.name, action, value }, options);
  }
}

/**
 * Set device capability
 */
async function setCapability(name, capability, value, options) {
  const client = createClient();
  const device = await client.getDevice(name, options);

  if (!(device.capabilities || []).includes(capability)) {
    throw cliError('CAPABILITY_NOT_SUPPORTED', `device '${device.name}' does not support capability '${capability}'`, {
      device: { id: device.id, name: device.name },
      capability,
      available: device.capabilities || [],
    });
  }

  const capObj = device.capabilitiesObj?.[capability];
  const declaredType = capObj?.type;
  const inferredType = capObj && 'value' in capObj ? typeof capObj.value : undefined;
  const type = declaredType || inferredType;

  let parsedValue = value;

  if (type === 'number') {
    parsedValue = parseFloat(value);
    if (Number.isNaN(parsedValue)) {
      throw cliError('INVALID_VALUE', `invalid number for '${capability}': '${value}'`, {
        device: { id: device.id, name: device.name },
        capability,
        value,
        expectedType: 'number',
      });
    }
  } else if (type === 'boolean') {
    const b = parseBoolean(value);
    if (b === null) {
      throw cliError('INVALID_VALUE', `invalid boolean for '${capability}': '${value}' (use true/false/on/off/1/0)`, {
        device: { id: device.id, name: device.name },
        capability,
        value,
        expectedType: 'boolean',
      });
    }
    parsedValue = b;
  }

  await client.setCapability(device.id, capability, parsedValue);

  if (!options.json) {
    console.log(chalk.green(`✓ Set ${device.name}.${capability} = ${parsedValue}`));
  } else {
    output({
      success: true,
      device: device.name,
      capability,
      value: parsedValue,
    }, options);
  }
}

/**
 * Get device capability value
 */
async function getCapability(name, capability, options) {
  const client = createClient();
  const device = await client.getDevice(name, options);

  if (!(device.capabilities || []).includes(capability)) {
    throw cliError('CAPABILITY_NOT_SUPPORTED', `device '${device.name}' does not support capability '${capability}'`, {
      device: { id: device.id, name: device.name },
      capability,
      available: device.capabilities || [],
    });
  }

  const value = await client.getCapability(device.id, capability);

  if (!options.json) {
    console.log(chalk.blue(`${device.name}.${capability} = ${value}`));
  } else {
    output({ device: device.name, capability, value }, options);
  }
}

/**
 * Inspect a device (capabilities + metadata + current values)
 */
async function inspectDevice(name, options) {
  const client = createClient();
  const device = await client.getDevice(name, options);

  if (options.json) {
    output(device, options);
    return;
  }

  console.log(chalk.bold(`\n🔎 Device: ${device.name}\n`));
  console.log(`  ${chalk.cyan('ID:')} ${device.id}`);
  console.log(`  ${chalk.cyan('Class:')} ${device.class}`);
  console.log(`  ${chalk.cyan('Zone:')} ${device.zoneName || device.zoneId || '-'}`);
  console.log(`  ${chalk.cyan('Available:')} ${device.available ? chalk.green('yes') : chalk.red('no')}`);
  console.log('');

  const table = new Table({
    head: [chalk.cyan('Capability'), chalk.cyan('Value'), chalk.cyan('Units'), chalk.cyan('Type')],
    colWidths: [30, 25, 15, 12],
  });

  for (const capId of device.capabilities || []) {
    const cap = device.capabilitiesObj?.[capId];
    table.push([
      capId,
      cap?.value === undefined ? '-' : String(cap.value),
      cap?.units || '-',
      cap?.type || (cap && 'value' in cap ? typeof cap.value : '-'),
    ]);
  }

  console.log(table.toString());
}

/**
 * Get all current capability values for a device
 */
async function getDeviceValues(name, options) {
  const client = createClient();
  const device = await client.getDevice(name, options);

  const data = {
    id: device.id,
    name: device.name,
    zoneId: device.zoneId,
    zoneName: device.zoneName,
    class: device.class,
    available: device.available,
    ready: device.ready,
    values: device.values,
    capabilitiesObj: device.capabilitiesObj,
  };

  if (options.raw && device.raw) {
    data.raw = device.raw;
  }

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.bold(`\n📟 Values: ${device.name}\n`));

  const table = new Table({
    head: [chalk.cyan('Capability'), chalk.cyan('Value'), chalk.cyan('Units')],
    colWidths: [30, 30, 15],
  });

  for (const [capId, capValue] of Object.entries(device.values || {})) {
    const units = device.capabilitiesObj?.[capId]?.units || '-';
    table.push([capId, capValue === undefined ? '-' : String(capValue), units]);
  }

  console.log(table.toString());
}

/**
 * List all flows
 */
async function listFlows(options) {
  const client = createClient();
  const flows = options.match
    ? await client.searchFlows(options.match, options)
    : await client.getFlows(options);

  if (options.json) {
    output(flows, options);
    return;
  }

  const table = new Table({
    head: [
      chalk.cyan('Name'),
      chalk.cyan('ID'),
      chalk.cyan('Enabled'),
      chalk.cyan('Folder'),
    ],
    colWidths: [40, 30, 10, 20],
  });

  for (const flow of flows) {
    const enabled = flow.enabled ? chalk.green('✓') : chalk.red('✗');

    table.push([
      flow.name,
      flow.id ? flow.id.substring(0, 20) + '...' : '-',
      enabled,
      flow.folder || '-',
    ]);
  }

  console.log(chalk.bold(`\n⚡ Found ${flows.length} flows:\n`));
  console.log(table.toString());
}

/**
 * Trigger a flow
 */
async function triggerFlow(name, options) {
  const client = createClient();
  const flow = await client.triggerFlow(name, options);

  if (!options.json) {
    console.log(chalk.green(`✓ Triggered flow: ${flow.name}`));
  } else {
    output({ success: true, flow: flow.name, id: flow.id }, options);
  }
}

/**
 * List zones
 */
async function listZones(options) {
  const client = createClient();
  const zones = await client.getZones(options);

  if (options.json) {
    output(zones, options);
    return;
  }

  const table = new Table({
    head: [
      chalk.cyan('Name'),
      chalk.cyan('ID'),
      chalk.cyan('Icon'),
    ],
    colWidths: [30, 30, 20],
  });

  for (const zone of zones) {
    table.push([
      zone.name,
      zone.id ? zone.id.substring(0, 20) + '...' : '-',
      zone.icon || '-',
    ]);
  }

  console.log(chalk.bold(`\n🏠 Found ${zones.length} zones:\n`));
  console.log(table.toString());
}

/**
 * Show connection status
 */
async function showStatus(options) {
  const client = createClient();
  const status = await client.getStatus();

  if (options.json) {
    output(status, options);
    return;
  }

  console.log(chalk.bold('\n🏠 Homey Status:\n'));
  console.log(`  ${chalk.cyan('Name:')} ${status.name}`);
  console.log(`  ${chalk.cyan('Connection:')} ${status.connectionMode || '-'}${status.address ? ` (${status.address})` : ''}`);
  console.log(`  ${chalk.cyan('Platform:')} ${status.platform} ${status.platformVersion ?? ''}`);
  console.log(`  ${chalk.cyan('Hostname:')} ${status.hostname || '-'}`);
  console.log(`  ${chalk.cyan('Homey ID:')} ${status.homeyId || status.cloudId || '-'}`);
  console.log(`  ${chalk.cyan('Status:')} ${chalk.green('✓ Connected')}\n`);
}

/**
 * Save token to ~/.homey/config.json
 */
function validateTokenAsciiNoWhitespace(token, label) {
  const t = String(token || '');
  if (!t.trim()) throw cliError('INVALID_VALUE', `${label} token is required`);
  if (/\s/.test(t)) {
    throw cliError('INVALID_VALUE', `${label} token contains whitespace (did you paste the wrong thing?)`);
  }
  // Be conservative: HTTP Authorization headers must be ASCII-ish; reject obvious non-printable chars.
  if (!/^[\x21-\x7E]+$/.test(t)) {
    throw cliError('INVALID_VALUE', `${label} token contains non-ASCII / non-printable characters (paste again)`, {
      hint: 'use --stdin or --prompt and paste only the token value',
    });
  }
}

async function authSetToken(token, options) {
  const t = String(token || '').trim();
  if (!t) {
    throw cliError('INVALID_VALUE', 'token is required');
  }
  validateTokenAsciiNoWhitespace(t, 'cloud');

  // Homey Web App "local API key" is typically a colon-separated triple-part token.
  // That token is NOT a cloud bearer token; using it in cloud mode yields confusing server errors.
  const cloudParts = t.split(':');
  if (cloudParts.length >= 3) {
    throw cliError(
      'INVALID_VALUE',
      'this looks like a local Homey API key (colon-separated). Use: homeycli auth set-local (local/LAN) instead of set-token (cloud).'
    );
  }

  config.saveToken(t);

  const info = config.getTokenInfo();
  const data = { saved: true, kind: 'cloud', source: info.source, path: info.path };

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.green('✓ Cloud token saved'));
  console.log(`  ${chalk.cyan('Path:')} ${info.path}`);
}

/**
 * Save local Homey connection settings to config.
 */
async function authSetLocal(token, options) {
  let address = String(options.address || '').trim();
  if (!address) {
    address = String(config.getLocalAddressInfo().address || '').trim();
  }
  if (!address) {
    throw cliError(
      'INVALID_VALUE',
      'address is required (use --address http://<homey-ip> or run: homeycli auth discover-local --save)'
    );
  }

  const t = String(token || '').trim();
  if (!t) {
    throw cliError('INVALID_VALUE', 'token is required');
  }

  validateTokenAsciiNoWhitespace(t, 'local');

  // Local keys are typically triple-part values separated by ':'.
  const localParts = t.split(':');
  if (localParts.length < 3) {
    throw cliError(
      'INVALID_VALUE',
      'local token format looks wrong (expected a colon-separated API key from the Homey Web App). If you are hosting remotely, use: homeycli auth set-token (cloud) instead.'
    );
  }

  config.saveLocalConfig({ address, token: t });

  const info = config.getConnectionInfo();
  const data = {
    saved: true,
    kind: 'local',
    address,
    path: info.path,
  };

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.green('✓ Local Homey config saved'));
  console.log(`  ${chalk.cyan('Address:')} ${address}`);
  console.log(`  ${chalk.cyan('Path:')} ${info.path}`);
}

/**
 * Set the preferred connection mode in config (auto|local|cloud).
 * (Can be overridden by env HOMEY_MODE)
 */
async function authSetMode(mode, options) {
  const m = String(mode || '').trim().toLowerCase();
  if (!['auto', 'local', 'cloud'].includes(m)) {
    throw cliError('INVALID_VALUE', "mode must be one of: auto, local, cloud");
  }

  const path = config.saveMode(m);
  const data = { saved: true, mode: m, path };

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.green('✓ Mode saved'));
  console.log(`  ${chalk.cyan('Mode:')} ${m}`);
  console.log(`  ${chalk.cyan('Path:')} ${path}`);
}

/**
 * Discover local Homey address via mDNS and optionally save it.
 */
async function authDiscoverLocal(options) {
  const timeoutMs = Number.isFinite(options.timeout) ? options.timeout : undefined;
  const save = Boolean(options.save);
  const pick = Number.isFinite(options.pick) ? options.pick : null;
  const pickHomeyId = options.homeyId ? String(options.homeyId).trim() : null;

  const found = await discoverLocalHomeys({ timeoutMs });
  requireDiscovered(found);

  // Dedupe by homeyId if present (else by address).
  const byId = new Map();
  for (const c of found) {
    const key = c.homeyId || c.address;
    if (!byId.has(key)) byId.set(key, c);
  }
  const candidates = Array.from(byId.values()).sort((a, b) => {
    const aid = a.homeyId || '';
    const bid = b.homeyId || '';
    if (aid !== bid) return aid.localeCompare(bid);
    return String(a.address).localeCompare(String(b.address));
  });

  if (save) {
    let chosen = null;

    if (pickHomeyId) {
      const matches = candidates.filter((c) => c.homeyId === pickHomeyId);
      if (matches.length === 1) chosen = matches[0];
      else if (matches.length === 0) {
        throw cliError('NOT_FOUND', `no discovered local Homey matches homeyId '${pickHomeyId}'`, {
          candidates: formatCandidates(candidates),
        });
      } else {
        throw cliError('AMBIGUOUS', `multiple discovered candidates match homeyId '${pickHomeyId}'`, {
          candidates: formatCandidates(matches),
        });
      }
    } else if (pick !== null) {
      if (!Number.isInteger(pick) || pick < 1 || pick > candidates.length) {
        throw cliError('INVALID_VALUE', `pick must be an integer between 1 and ${candidates.length}`, {
          candidates: formatCandidates(candidates),
        });
      }
      chosen = candidates[pick - 1];
    } else if (candidates.length === 1) {
      chosen = candidates[0];
    } else {
      throw cliError(
        'AMBIGUOUS',
        `found ${candidates.length} local Homey candidates; choose one with --pick <n> or --homey-id <id> (or set --address manually)`,
        { candidates: formatCandidates(candidates) }
      );
    }

    const path = config.saveLocalAddress(chosen.address);

    const data = {
      discovered: true,
      saved: true,
      kind: 'local',
      address: chosen.address,
      homeyId: chosen.homeyId,
      path,
    };

    if (options.json) {
      output(data, options);
      return;
    }

    console.log(chalk.green('✓ Local Homey address discovered and saved'));
    console.log(`  ${chalk.cyan('Address:')} ${chosen.address}`);
    if (chosen.homeyId) console.log(`  ${chalk.cyan('Homey ID:')} ${chosen.homeyId}`);
    console.log(`  ${chalk.cyan('Path:')} ${path}`);
    return;
  }

  const data = { discovered: true, candidates: formatCandidates(candidates) };
  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.bold(`\n🔎 Discovered ${candidates.length} local Homey candidate(s):\n`));
  for (const c of formatCandidates(candidates)) {
    console.log(`  [${c.index}] ${c.address}${c.homeyId ? `  (id: ${c.homeyId})` : ''}`);
  }
  console.log('');
}

async function authClearCloud(options) {
  const path = config.clearCloudToken();
  const data = { cleared: true, kind: 'cloud', path };
  if (options.json) return output(data, options);
  console.log(chalk.green('✓ Cloud token cleared'));
  console.log(`  ${chalk.cyan('Path:')} ${path}`);
}

async function authClearLocal(options) {
  const path = config.clearLocalConfig();
  const data = { cleared: true, kind: 'local', path };
  if (options.json) return output(data, options);
  console.log(chalk.green('✓ Local config cleared'));
  console.log(`  ${chalk.cyan('Path:')} ${path}`);
}

/**
 * Show auth status for local + cloud (never prints full tokens).
 */
async function authStatus(options) {
  const modeInfo = config.getModeInfo();
  const conn = config.getConnectionInfo();
  const cloud = config.getCloudTokenInfo();
  const localToken = config.getLocalTokenInfo();
  const localAddress = config.getLocalAddressInfo();

  const data = {
    modeWanted: modeInfo.mode,
    modeWantedSource: modeInfo.source,
    modeSelected: conn.modeSelected,
    path: conn.path,
    local: {
      addressPresent: Boolean(localAddress.address),
      tokenPresent: Boolean(localToken.token),
      address: localAddress.address,
      addressSource: localAddress.source,
      tokenSource: localToken.source,
    },
    cloud: {
      tokenPresent: Boolean(cloud.token),
      tokenSource: cloud.source,
    },
  };

  if (options.json) {
    output(data, options);
    return;
  }

  const localLast4 = localToken.token ? localToken.token.slice(-4) : null;
  const cloudLast4 = cloud.token ? cloud.token.slice(-4) : null;

  console.log(chalk.bold('\n🔐 Auth Status:\n'));
  console.log(`  ${chalk.cyan('Mode (wanted):')} ${data.modeWanted} (${data.modeWantedSource})`);
  console.log(`  ${chalk.cyan('Mode (selected):')} ${data.modeSelected}`);
  console.log(`  ${chalk.cyan('Config path:')} ${data.path}`);

  console.log(chalk.bold('\n  Local (LAN/VPN):'));
  console.log(`    ${chalk.cyan('Address:')} ${data.local.address || '-'} (${data.local.addressSource || '-'})`);
  console.log(`    ${chalk.cyan('Token present:')} ${data.local.tokenPresent ? chalk.green('yes') : chalk.red('no')} (${data.local.tokenSource || '-'})`);
  if (localLast4) console.log(`    ${chalk.cyan('Token last4:')} ${localLast4}`);

  console.log(chalk.bold('\n  Cloud (remote):'));
  console.log(`    ${chalk.cyan('Token present:')} ${data.cloud.tokenPresent ? chalk.green('yes') : chalk.red('no')} (${data.cloud.tokenSource || '-'})`);
  if (cloudLast4) console.log(`    ${chalk.cyan('Token last4:')} ${cloudLast4}`);

  console.log('\n  Setup commands:');
  console.log('    Local:  echo "<LOCAL_API_KEY>" | homeycli auth set-local --address http://<homey-ip> --stdin');
  console.log('    Cloud:  echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin');
  console.log('');
}

/**
 * Snapshot of the world (status + zones + devices). Flows intentionally excluded by default.
 */
async function snapshot(options) {
  const client = createClient();

  // Parallelize the network calls to reduce latency.
  const [status, zones, devices] = await Promise.all([
    client.getStatus(),
    client.getZones(options),
    client.getDevices(options),
  ]);

  const data = { status, zones, devices };

  if (options.includeFlows) {
    data.flows = await client.getFlows(options);
  }

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.bold('\n📸 Snapshot:\n'));
  console.log(`  ${chalk.cyan('Homey:')} ${status.name} (${status.platform} ${status.platformVersion})`);
  console.log(`  ${chalk.cyan('Devices:')} ${devices.length}`);
  console.log(`  ${chalk.cyan('Zones:')} ${zones.length}`);
  if (data.flows) console.log(`  ${chalk.cyan('Flows:')} ${data.flows.length}`);
  console.log('');
}

module.exports = {
  listDevices,
  controlDevice,
  setCapability,
  getCapability,
  getDeviceValues,
  inspectDevice,
  listFlows,
  triggerFlow,
  listZones,
  showStatus,
  snapshot,

  authSetToken,
  authSetLocal,
  authDiscoverLocal,
  authSetMode,
  authClearCloud,
  authClearLocal,
  authStatus,
};
