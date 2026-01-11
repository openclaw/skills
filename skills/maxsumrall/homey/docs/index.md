# homeycli

Control Athom Homey devices from the command line via local (LAN/VPN) or cloud APIs.

This tool is designed to be called by an LLM/agent (ClawdHub skill), so it prioritizes:

- machine-readable JSON (`--json`)
- returning full device state (multi-sensor friendly)
- safe disambiguation (if a query matches >1 device, it errors and returns candidate IDs)

## Install

```bash
npm install
chmod +x bin/homeycli.js
```

## Auth

Local mode (LAN/VPN):

```bash
homeycli auth discover-local --save --pick 1

echo "LOCAL_API_KEY" | homeycli auth set-local --stdin
# or interactive (hidden input): homeycli auth set-local --prompt
```

Cloud mode (remote/headless):

```bash
echo "CLOUD_TOKEN" | homeycli auth set-token --stdin
# or interactive (hidden input): homeycli auth set-token --prompt
```

Note: the colon-separated triple-part key from the Homey Web App is for **local mode** only.

Check status:

```bash
homeycli auth status --json
```

## Recommended: snapshot

```bash
homeycli snapshot --json
homeycli snapshot --json --include-flows
```

## Devices

```bash
homeycli devices --json
homeycli devices --match "kitchen" --json

homeycli device "Kitchen Light" values --json
homeycli device <device-id> set dim 0.7 --json
```

## Flows

```bash
homeycli flows --json
homeycli flow trigger "Good Night" --json
```

See the README for more.

For agent integrations, also see: `docs/output.md` (stable JSON contract).
