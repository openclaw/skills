#!/usr/bin/env node

const { program } = require('commander');
const commands = require('../lib/commands');

const pkg = require('../package.json');

program
  .name('homeycli')
  .description('Control Athom Homey smart home devices via Cloud API')
  .version(pkg.version);

// Global options
program
  .option('--json', 'Output JSON (stdout) instead of formatted text')
  .option('--raw', 'Include raw Homey API objects in JSON output (very verbose)')
  .option('--threshold <n>', 'Fuzzy match threshold (default: 5)', (v) => parseInt(v, 10));

function exitCodeForError(err) {
  switch (err?.code) {
    case 'NO_TOKEN':
      return 2;
    case 'NOT_FOUND':
      return 3;
    case 'AMBIGUOUS':
      return 4;
    case 'CAPABILITY_NOT_SUPPORTED':
    case 'INVALID_VALUE':
      return 5;
    default:
      return 1;
  }
}

function printError(err, opts) {
  const message = err?.message || String(err);
  const code = err?.code || 'ERROR';
  const details = err?.details;

  if (opts?.json) {
    const payload = { error: { code, message } };
    if (details !== undefined) payload.error.details = details;
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.error(`error: ${message}`);

  const candidates = details?.candidates;
  if (Array.isArray(candidates) && candidates.length) {
    console.error('candidates:');
    for (const c of candidates) {
      if (c.id && c.name) {
        console.error(`  ${c.id}  ${c.name}`);
      } else if (c.name) {
        console.error(`  ${c.name}`);
      } else {
        console.error(`  ${JSON.stringify(c)}`);
      }
    }
  }
}

async function runOrExit(fn) {
  const opts = program.opts();
  try {
    await fn(opts);
  } catch (err) {
    printError(err, opts);
    process.exit(exitCodeForError(err));
  }
}

function commandOpts(maybeCommandOrOpts) {
  if (maybeCommandOrOpts && typeof maybeCommandOrOpts.opts === 'function') {
    return maybeCommandOrOpts.opts();
  }
  // Commander may pass plain options object in some cases.
  if (maybeCommandOrOpts && typeof maybeCommandOrOpts === 'object') {
    return maybeCommandOrOpts;
  }
  return {};
}

// Devices command
program
  .command('devices')
  .description('List devices (latest state)')
  .option('--match <query>', 'Filter devices by name (returns multiple matches)')
  .action((maybeCmd) => runOrExit((opts) => commands.listDevices({ ...opts, ...commandOpts(maybeCmd) })));

// Device operations
program
  .command('device <nameOrId> <action> [capability] [value]')
  .description('Device operations (on/off/set/get/values/inspect)')
  .action((nameOrId, action, capability, value) =>
    runOrExit((opts) => {
      if (action === 'on') return commands.controlDevice(nameOrId, 'on', opts);
      if (action === 'off') return commands.controlDevice(nameOrId, 'off', opts);
      if (action === 'set') {
        if (!capability || value === undefined) {
          throw new Error('usage: device <nameOrId> set <capability> <value>');
        }
        return commands.setCapability(nameOrId, capability, value, opts);
      }
      if (action === 'get') {
        if (!capability) return commands.getDeviceValues(nameOrId, opts);
        return commands.getCapability(nameOrId, capability, opts);
      }
      if (action === 'values') return commands.getDeviceValues(nameOrId, opts);
      if (action === 'inspect') return commands.inspectDevice(nameOrId, opts);

      throw new Error('invalid action. Use: on, off, set <capability> <value>, get [capability], values, inspect');
    })
  );

// Flows command
program
  .command('flows')
  .description('List flows')
  .option('--match <query>', 'Filter flows by name (returns multiple matches)')
  .action((maybeCmd) => runOrExit((opts) => commands.listFlows({ ...opts, ...commandOpts(maybeCmd) })));

program
  .command('flow <action> <nameOrId>')
  .description('Flow operations (trigger)')
  .action((action, nameOrId) =>
    runOrExit((opts) => {
      if (action === 'trigger') return commands.triggerFlow(nameOrId, opts);
      throw new Error('invalid action. Use: trigger');
    })
  );

// Snapshot command
program
  .command('snapshot')
  .description('Get a point-in-time snapshot (status + zones + devices)')
  .option('--include-flows', 'Also include flows (can be large)')
  .action((maybeCmd) => runOrExit((opts) => commands.snapshot({ ...opts, ...commandOpts(maybeCmd) })));

// Zones command
program
  .command('zones')
  .description('List all zones/rooms')
  .action(() => runOrExit((opts) => commands.listZones(opts)));

// Status command
program
  .command('status')
  .description('Show Homey connection status and info')
  .action(() => runOrExit((opts) => commands.showStatus(opts)));

// Auth helper commands
program
  .command('auth <action> [token]')
  .description('Authentication helpers (set-token, status)')
  .action((action, token) =>
    runOrExit((opts) => {
      if (action === 'set-token') return commands.authSetToken(token, opts);
      if (action === 'status') return commands.authStatus(opts);
      throw new Error('invalid auth action. Use: set-token <token>, status');
    })
  );

program.parse();
