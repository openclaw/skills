const chalk = require('chalk');
const Table = require('cli-table3');
const HomeyClient = require('./client');
const config = require('./config');

/**
 * Create Homey client from config
 */
const { cliError } = require('./errors');

function createClient() {
  const token = config.getToken();
  if (!token) {
    throw cliError(
      'NO_TOKEN',
      'no Homey token found (set HOMEY_TOKEN or write ~/.homey/config.json)',
      { help: 'Get a token from https://tools.developer.homey.app/api/clients' }
    );
  }
  return new HomeyClient(token);
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
  console.log(`  ${chalk.cyan('Platform:')} ${status.platform} ${status.platformVersion}`);
  console.log(`  ${chalk.cyan('Hostname:')} ${status.hostname}`);
  console.log(`  ${chalk.cyan('Cloud ID:')} ${status.cloudId}`);
  console.log(`  ${chalk.cyan('Status:')} ${chalk.green('✓ Connected')}\n`);
}

/**
 * Save token to ~/.homey/config.json
 */
async function authSetToken(token, options) {
  const t = String(token || '').trim();
  if (!t) {
    throw cliError('INVALID_VALUE', 'token is required');
  }

  config.saveToken(t);

  const info = config.getTokenInfo();
  const data = { saved: true, source: info.source, path: info.path };

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.green('✓ Token saved'));
  console.log(`  ${chalk.cyan('Path:')} ${info.path}`);
}

/**
 * Show where token is coming from (never prints the token)
 */
async function authStatus(options) {
  const info = config.getTokenInfo();
  const data = {
    tokenPresent: Boolean(info.token),
    source: info.source,
    path: info.path,
    tokenLast4: info.token ? info.token.slice(-4) : null,
  };

  if (options.json) {
    output(data, options);
    return;
  }

  console.log(chalk.bold('\n🔐 Auth Status:\n'));
  console.log(`  ${chalk.cyan('Token present:')} ${data.tokenPresent ? chalk.green('yes') : chalk.red('no')}`);
  console.log(`  ${chalk.cyan('Source:')} ${data.source || '-'}`);
  console.log(`  ${chalk.cyan('Config path:')} ${data.path}`);
  if (data.tokenLast4) {
    console.log(`  ${chalk.cyan('Token last4:')} ${data.tokenLast4}`);
  }
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
  authStatus,
};
