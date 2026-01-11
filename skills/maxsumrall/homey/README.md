# homeycli

Docs: https://maxsumrall.github.io/homeycli/

Agent integration contract (stable JSON fields/errors): `docs/output.md`

Control Athom Homey smart home devices from the command line via local (LAN/VPN) or cloud APIs.

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

### 2. Choose connection mode

This CLI supports **local** and **cloud** connections.

#### Local mode (LAN/VPN)

Use this when the machine running `homeycli` can reach your Homey on the local network (or via VPN).

1. In the **Homey Web App**, generate a **local API key**.
2. Find your Homey local address (e.g. `http://192.168.1.50`).

#### Cloud mode (remote/headless)

Use this when you run the agent on a VPS / outside your home network.

- Create a cloud token in Homey Developer Tools:
  https://tools.developer.homey.app/api/clients

Important:
- The **colon-separated triple-part key** from the Homey Web App is a **local** API key.
  It will not work as a cloud token.

(Advanced: you can also set up an OAuth client + flow in Developer Tools; the CLI currently supports token-based auth best.)

### 3. Configure

Default is `HOMEY_MODE=auto`:
- if a local address is configured, it uses **local**
- otherwise it uses **cloud**

#### Configure local

```bash
# 1) discover local address (mDNS, best effort)
homeycli auth discover-local --json
homeycli auth discover-local --save --pick 1

# 2) save local API key (address is reused if already stored)
echo "LOCAL_API_KEY" | homeycli auth set-local --stdin
# or interactive (hidden input): homeycli auth set-local --prompt

# (or set address explicitly)
echo "LOCAL_API_KEY" | homeycli auth set-local --address http://<homey-ip> --stdin
```

#### Configure cloud

```bash
echo "CLOUD_TOKEN" | homeycli auth set-token --stdin
# or interactive (hidden input): homeycli auth set-token --prompt
```

#### Force a mode (optional)

```bash
homeycli auth set-mode auto
homeycli auth set-mode local
homeycli auth set-mode cloud
```

#### Env vars (override config)

```bash
export HOMEY_MODE=auto|local|cloud
export HOMEY_ADDRESS="http://192.168.1.50"      # local
export HOMEY_LOCAL_TOKEN="..."                  # local
export HOMEY_TOKEN="..."                        # cloud
```

Manual config file (not recommended; use `homeycli auth ...` instead):

```bash
mkdir -p ~/.homey
cat > ~/.homey/config.json <<'JSON'
{
  "mode": "auto",
  "local": { "address": "http://192.168.1.50", "token": "LOCAL_API_KEY" },
  "cloud": { "token": "CLOUD_TOKEN" }
}
JSON
```

Legacy config is still supported for cloud token only:

```json
{ "token": "CLOUD_TOKEN" }
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

## Authentication / connection modes

This CLI supports **local** and **cloud** connections:

- **Local (LAN/VPN)**: connect directly to your Homey using a local API key generated in the Homey Web App.
  - Requires: `HOMEY_ADDRESS` + local token (`HOMEY_LOCAL_TOKEN` or `homeycli auth set-local ...`)
- **Cloud (remote/headless)**: connect via Athom/Homey cloud using a cloud token (PAT) created in Developer Tools.
  - Requires: `HOMEY_TOKEN` (or `homeycli auth set-token ...`)

Default `HOMEY_MODE=auto` prefers local when an address is configured.

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

### Releasing (version bumps)

Tag pushes (`v*`) are treated as releases. The publish script enforces that the git tag version matches `package.json`.

Recommended:

```bash
npm run release:patch   # or release:minor / release:major

# pushes the release commit + tag (vX.Y.Z)
git push origin HEAD --follow-tags
```

This triggers the `publish-clawdhub` workflow.

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

**No auth configured:**

Local (LAN/VPN):
- `echo "<LOCAL_API_KEY>" | homeycli auth set-local --address http://<homey-ip> --stdin`

Cloud (remote/headless):
- `echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin`
- Cloud tokens can be created in Developer Tools: https://tools.developer.homey.app/api/clients

**Device not found / ambiguous:**
- Use `homeycli devices --json` (or `--match <query>`) to find the exact device `id`
- If a name matches multiple devices, the CLI returns an error with candidate IDs (use the ID to disambiguate)

**Connection errors:**

- Local mode:
  - ensure `HOMEY_ADDRESS` is reachable from where you run `homeycli` (LAN/VPN)
  - ensure the local API key is valid
- Cloud mode:
  - check internet connection
  - verify the cloud token is valid
  - ensure Homey is online in the cloud

## License

MIT

## Author

Max Sumrall (@maxsumrall)

Built for Clawdbot/ClawdHub 🦞
