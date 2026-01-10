# Testing Guide

How to test the Homey CLI skill.

## Prerequisites

1. **Homey Device** - You need access to a physical Homey Pro, Homey Cloud, or Homey Bridge
2. **Bearer Token** - Get from https://tools.developer.homey.app/api/clients
3. **Dependencies Installed** - Run `npm install` in this directory

## Setup

```bash
# Navigate to skill directory
cd path/to/homeycli

# Install dependencies (if not already done)
npm install

# Make CLI executable (if not already done)
chmod +x bin/homeycli.js

# Set your token
export HOMEY_TOKEN="your-bearer-token-here"
```

## Basic Tests

### 1. Test Help System
```bash
# Should show general help
./bin/homeycli.js --help

# Should show device command help
./bin/homeycli.js device --help

# Should show flow command help
./bin/homeycli.js flow --help
```

Expected: Help text displays correctly with all commands listed.

### 2. Test Connection
```bash
# Should connect and show Homey info
./bin/homeycli.js status

# JSON output
./bin/homeycli.js status --json
```

Expected: Connection succeeds, shows Homey name, platform, version.

### 3. Test Device Listing
```bash
# Should list all devices in a table
./bin/homeycli.js devices

# Should output JSON
./bin/homeycli.js devices --json
```

Expected: Devices displayed with name, zone, class, capabilities, state.

### 4. Test Device Control
```bash
# Replace "Device Name" with an actual device from your Homey

# Turn on
./bin/homeycli.js device "Living Room Light" on

# Turn off
./bin/homeycli.js device "Living Room Light" off

# Set capability (adjust based on your device)
./bin/homeycli.js device "Dimmer" set dim 0.5

# Get capability
./bin/homeycli.js device "Sensor" get measure_temperature
```

Expected: Commands execute successfully, devices respond.

### 5. Test Fuzzy Matching
```bash
# Use partial/misspelled device name
./bin/homeycli.js device "living light" on
```

Expected: Should find closest match and control it.

### 6. Test Flows
```bash
# List flows
./bin/homeycli.js flows

# Trigger a flow (use actual flow name)
./bin/homeycli.js flow trigger "Good Morning"
```

Expected: Flows listed, trigger executes successfully.

### 7. Test Zones
```bash
# List zones
./bin/homeycli.js zones

# JSON output
./bin/homeycli.js zones --json
```

Expected: All rooms/zones displayed.

## Error Cases to Test

### 1. Missing Token
```bash
# Unset token temporarily
unset HOMEY_TOKEN

# Should show helpful error
./bin/homeycli.js status
```

Expected: Clear error message with instructions to set token.

### 2. Invalid Device Name
```bash
# Try non-existent device
./bin/homeycli.js device "NonExistentDevice" on
```

Expected: "Device not found" error, possibly with suggestions.

### 3. Invalid Capability
```bash
# Try to set capability that device doesn't support
./bin/homeycli.js device "Motion Sensor" set onoff true
```

Expected: Error showing device doesn't support that capability, list available ones.

### 4. Invalid Flow Name
```bash
# Try non-existent flow
./bin/homeycli.js flow trigger "NonExistentFlow"
```

Expected: "Flow not found" error.

## Integration Tests

### 1. JSON Output Parsing
```bash
# Should produce valid JSON that can be parsed
./bin/homeycli.js devices --json | jq '.[0].name'
./bin/homeycli.js status --json | jq '.name'
```

Expected: Valid JSON that jq can parse successfully.

### 2. Chained Commands
```bash
# Run multiple commands in sequence
./bin/homeycli.js device "Light" on && \
./bin/homeycli.js device "Light" set dim 0.5 && \
./bin/homeycli.js device "Light" off
```

Expected: All commands execute in order.


## Manual Testing Checklist

- [ ] Help displays correctly for all commands
- [ ] Connection to Homey succeeds
- [ ] Device listing shows all devices
- [ ] Device control (on/off) works
- [ ] Capability get/set works
- [ ] Fuzzy matching finds devices
- [ ] Flow listing works
- [ ] Flow triggering works
- [ ] Zone listing works
- [ ] JSON output is valid
- [ ] Error messages are helpful
- [ ] Missing token shows clear error
- [ ] Invalid device shows helpful error
- [ ] Invalid capability shows available ones

## Automated Tests (Optional)

You can create automated tests if you have a test Homey:

```javascript
// test/integration.test.js (example)
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

describe('Homey CLI', () => {
  it('should show status', async () => {
    const { stdout } = await execAsync('./bin/homeycli.js status');
    expect(stdout).toContain('Connected');
  });

  it('should list devices', async () => {
    const { stdout } = await execAsync('./bin/homeycli.js devices --json');
    const devices = JSON.parse(stdout);
    expect(Array.isArray(devices)).toBe(true);
  });
});
```

## Troubleshooting Tests

If tests fail:

1. **Check token** - `echo $HOMEY_TOKEN`
2. **Check Homey online** - Visit https://my.homey.app
3. **Check dependencies** - `npm list`
4. **Check Node version** - `node --version` (should be >= 18)

## Performance Benchmarks

Expected performance on M-series Mac:

- First command (cold start): ~2-3 seconds
- Device listing: ~1-2 seconds
- Device control: ~0.5-1 seconds
- Flow trigger: ~0.5-1 seconds

## Ready for Production?

Before publishing to ClawdHub:

- [ ] All manual tests pass
- [ ] Error handling is graceful
- [ ] Documentation is complete
- [ ] Examples work as shown
- [ ] JSON output is valid
- [ ] Performance is acceptable
- [ ] Code is clean and commented
- [ ] README is clear and helpful

## Next Steps

Once tested:

1. Test installation via Clawdbot: Install from skill directory
2. Test AI integration: Ask Clawdbot to control Homey devices
3. Gather feedback: Use for a few days, note issues
4. Publish to ClawdHub: Submit for community use

## Support

If you encounter issues:

1. Check Homey API status: https://status.athom.com
2. Verify token validity: https://tools.developer.homey.app/api/clients
3. Check Homey logs: https://my.homey.app → Settings → System → Logs
4. Review homey-api docs: https://athombv.github.io/node-homey-api/
