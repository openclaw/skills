# Command reference

## snapshot

```bash
homeycli snapshot --json
homeycli snapshot --json --include-flows
```

Returns a point-in-time snapshot:
- status
- zones
- devices (including `values` and `capabilitiesObj`)
- flows (optional)

## devices

```bash
homeycli devices --json
homeycli devices --match "kitchen" --json
```

## device

```bash
homeycli device <nameOrId> values --json
homeycli device <nameOrId> inspect --json
homeycli device <nameOrId> get <capability> --json
homeycli device <nameOrId> set <capability> <value> --json
homeycli device <nameOrId> on --json
homeycli device <nameOrId> off --json
```

Resolution order for `<nameOrId>` is deterministic:

1. direct id match
2. exact name match (case-insensitive)
3. substring match (case-insensitive)
4. fuzzy match (Levenshtein) if the best match is unique and within `--threshold` (default: 5)

If `<nameOrId>` matches more than one device at any step, the command fails with `AMBIGUOUS` and returns candidate IDs.

## flows

```bash
homeycli flows --json
homeycli flows --match "good" --json
```

## flow

```bash
homeycli flow trigger <nameOrId> --json
```

`<nameOrId>` resolution uses the same deterministic rules as devices (id → exact → substring → fuzzy within `--threshold`).

## zones

```bash
homeycli zones --json
```

## auth

Show current auth/config status:

```bash
homeycli auth status --json
```

### Local mode (LAN/VPN)

Save local Homey settings (recommended when the agent runs on your home network):

```bash
# 1) discover local address (best effort via mDNS)
homeycli auth discover-local --json

# save it (if multiple candidates, pick one)
homeycli auth discover-local --save --pick 1
# or: homeycli auth discover-local --save --homey-id <id>

# 2) store local API key (address is reused from config if already discovered)
echo "LOCAL_API_KEY" | homeycli auth set-local --stdin
# or interactive (hidden input): homeycli auth set-local --prompt

# (or set address explicitly)
echo "LOCAL_API_KEY" | homeycli auth set-local --address http://<homey-ip> --stdin
```

### Cloud mode (remote/headless)

Save cloud token (recommended for VPS/headless hosting):

```bash
echo "CLOUD_TOKEN" | homeycli auth set-token --stdin
# or interactive (hidden input): homeycli auth set-token --prompt
```

Note: the colon-separated triple-part key from the Homey Web App is for **local mode** only.

### Mode selection

By default, the CLI runs in `auto` mode (prefers local if an address is configured).
You can force a mode:

```bash
homeycli auth set-mode auto
homeycli auth set-mode local
homeycli auth set-mode cloud
```

### Clear

```bash
homeycli auth clear-local
homeycli auth clear-token
```

### Env vars (override config)

- `HOMEY_MODE=auto|local|cloud`
- `HOMEY_ADDRESS=http://...` (local)
- `HOMEY_LOCAL_TOKEN=...` (local)
- `HOMEY_TOKEN=...` (cloud)
