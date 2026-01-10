# homeycli

Control Athom Homey devices from the command line using the Homey Cloud API.

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

```bash
homeycli auth set-token "YOUR_TOKEN"
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
