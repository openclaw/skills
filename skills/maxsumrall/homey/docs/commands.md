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

If `<nameOrId>` matches more than one device, the command fails with `AMBIGUOUS` and returns candidate IDs.

## flows

```bash
homeycli flows --json
homeycli flows --match "good" --json
```

## flow

```bash
homeycli flow trigger <nameOrId> --json
```

## zones

```bash
homeycli zones --json
```

## auth

```bash
homeycli auth set-token "TOKEN"
homeycli auth status --json
```
