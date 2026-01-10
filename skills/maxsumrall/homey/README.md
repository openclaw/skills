# homeycli

Docs: https://maxsumrall.github.io/homeycli/


Control Athom Homey smart home devices from the command line using Cloud API with Bearer token authentication.

## Features

- ✅ List and control all Homey devices
- ✅ Trigger flows (automations)
- ✅ Query zones/rooms
- ✅ Fuzzy name matching (typo-tolerant)
- ✅ JSON output for AI/script parsing
- ✅ Pretty terminal tables

## Quick Start

### 1. Install Dependencies

Requires Node.js >= 18.

```bash
cd path/to/homeycli
npm install
```

### 2. Get Bearer Token

Visit https://tools.developer.homey.app/api/clients and create a Personal Access Token.

### 3. Configure

Set environment variable:
```bash
export HOMEY_TOKEN="your-bearer-token-here"
```

Or save to config file (recommended for tools/agents):
```bash
homeycli auth set-token "your-token-here"

# check auth status (never prints the token)
homeycli auth status
```

Manual config file (equivalent):
```bash
mkdir -p ~/.homey
echo '{"token":"your-token-here"}' > ~/.homey/config.json
```

### 4. Test

```bash
./bin/homeycli.js status
```

Or install globally:
```bash
npm link
homeycli status
```

## Usage Examples

### Snapshot (recommended for agents)
```bash
# One call: status + zones + all devices with latest values
homeycli snapshot --json

# If you also want flows
homeycli snapshot --json --include-flows
```

### List Devices
```bash
# All devices (includes latest capability values)
homeycli devices
homeycli devices --json

# Filter devices by name (returns multiple matches)
homeycli devices --match "kitchen" --json
```

### Control Devices
```bash
# Turn on/off
homeycli device "Living Room Light" on
homeycli device "Bedroom" off

# Set capabilities
homeycli device "Dimmer" set dim 0.5
homeycli device "Thermostat" set target_temperature 21
homeycli device "RGB Light" set light_hue 0.33

# Get capability values
homeycli device "Sensor" get measure_temperature

# Get all capability values for a device (useful for multi-sensors)
homeycli device "Living Room Air" values
homeycli device "Living Room Air" get
```

### Flows
```bash
# List flows
homeycli flows
homeycli flows --json

# Filter flows by name
homeycli flows --match "good" --json

# Trigger flow
homeycli flow trigger "Good Night"
homeycli flow trigger <flow-id>
```

### Zones
```bash
homeycli zones
```

## Integration with Clawdbot

This skill is designed for ClawdHub. Once installed via Clawdbot, the AI can:

- List devices and their current state
- Turn lights/switches on/off
- Adjust brightness, temperature, colors
- Trigger automation flows
- Query sensor values
- Organize actions by room/zone

Example AI commands:
- "Turn on the living room lights"
- "Set bedroom temperature to 21 degrees"
- "Trigger the Good Night flow"
- "What's the temperature in the kitchen?"

## Architecture

```
homeycli/
├── bin/
│   └── homeycli.js         # Main CLI executable
├── lib/
│   ├── client.js           # Homey API wrapper
│   ├── commands.js         # Command implementations
│   ├── fuzzy.js            # Fuzzy name matching
│   └── config.js           # Token/session management
├── package.json
├── SKILL.md                # Clawdbot skill definition
└── README.md               # This file
```

## Dependencies

- `homey-api` (v3.15.0) - Official Athom Homey API client
- `commander` (v12) - CLI framework
- `chalk` (v4) - Terminal colors
- `cli-table3` (v0.6) - Pretty tables

## Authentication

Uses Bearer token authentication (not OAuth). Tokens are:
- Obtained from https://tools.developer.homey.app/api/clients
- Stored in `HOMEY_TOKEN` env var or `~/.homey/config.json`

## Common Capabilities

- `onoff` - Power (boolean)
- `dim` - Brightness (0-1)
- `target_temperature` - Thermostat target (number)
- `measure_temperature` - Current temp (read-only)
- `light_hue` - Color hue (0-1)
- `light_saturation` - Color saturation (0-1)
- `locked` - Lock state (boolean)
- `volume_set` - Volume (0-1)

See `homeycli devices` for device-specific capabilities.

## CI publish to ClawdHub

This repo includes a GitHub Actions workflow to publish to ClawdHub using the official `clawdhub` CLI:

- Workflow: `.github/workflows/publish-clawdhub.yml`
- Trigger: manual (`workflow_dispatch`) or tag push (`v*`)

To enable it, add this GitHub repo secret:

- `CLAWDHUB_API_KEY` – ClawdHub API token (used by `clawdhub login --token ...`)

Notes:
- The workflow installs `clawdhub` pinned (see `CLAWDHUB_CLI_VERSION` in `.github/workflows/publish-clawdhub.yml`).
- The publish step is implemented in `scripts/publish-clawdhub.sh`.
- The default publish slug is taken from `SKILL.md` frontmatter (`name:`). You can override it via workflow inputs.

## Security (prevent secrets in git)

This repo is set up to catch accidental secret commits in GitHub (no local hook installs required):

1. **Enable GitHub Secret Scanning + Push Protection**
   - Repo → **Settings** → **Code security and analysis**
   - Turn on:
     - **Secret scanning**
     - **Push protection** (blocks pushes containing recognized secrets)

2. **CI secret scan**
   - GitHub Actions runs **gitleaks** on pull requests and on pushes to `main`.
   - Workflow: `.github/workflows/secret-scan.yml`

If you ever accidentally publish a token anyway, assume it’s compromised: revoke it in the Homey developer tools and rotate.

## Troubleshooting

**No token found:**
- Set `HOMEY_TOKEN` or create `~/.homey/config.json`
- Get token from: https://tools.developer.homey.app/api/clients

**Device not found / ambiguous:**
- Use `homeycli devices --json` (or `--match <query>`) to find the exact device `id`
- If a name matches multiple devices, the CLI returns an error with candidate IDs (use the ID to disambiguate)

**Connection errors:**
- Check internet connection
- Verify token is valid
- Ensure Homey is online in the cloud

## License

MIT

## Author

Max Sumrall (@maxsumrall)

Built for Clawdbot/ClawdHub 🦞
