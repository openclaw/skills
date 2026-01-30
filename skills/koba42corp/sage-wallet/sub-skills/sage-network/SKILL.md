---
name: sage-network
description: Sage network and peer settings. Manage peers, switch networks, configure sync settings, set change address.
---

# Sage Network & Peers

Network configuration and peer management.

## Endpoints

### Peer Management

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_peers` | `{}` | List connected peers |
| `add_peer` | `{"ip": "node.example.com:8444"}` | Add peer |
| `remove_peer` | `{"ip": "...", "ban": false}` | Remove/ban peer |
| `set_discover_peers` | `{"discover_peers": true}` | Toggle auto-discovery |
| `set_target_peers` | `{"target_peers": 8}` | Set target count |

### Network Settings

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_network` | `{}` | Get current network |
| `get_networks` | `{}` | List available networks |
| `set_network` | `{"name": "mainnet"}` | Switch network |
| `set_network_override` | `{"fingerprint": ..., "name": "testnet11"}` | Per-wallet override |

### Sync Settings

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `set_delta_sync` | `{"delta_sync": true}` | Toggle delta sync |
| `set_delta_sync_override` | `{"fingerprint": ..., "delta_sync": true}` | Per-wallet override |

### Address Settings

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `set_change_address` | `{"fingerprint": ..., "change_address": "xch1..."}` | Set change address |

## Peer Record Structure

```json
{
  "ip": "192.168.1.100:8444",
  "port": 8444,
  "peak_height": 1234567,
  "synced": true
}
```

## Network Response Structure

```json
{
  "network": {
    "name": "mainnet",
    "prefix": "xch",
    "default_port": 8444,
    "genesis_challenge": "0x..."
  },
  "kind": "mainnet"
}
```

Network kinds: `"mainnet"`, `"testnet"`, `"unknown"`

## Examples

```bash
# List peers
sage_rpc get_peers '{}'

# Add peer
sage_rpc add_peer '{"ip": "node.chia.net:8444"}'

# Remove and ban peer
sage_rpc remove_peer '{"ip": "192.168.1.50:8444", "ban": true}'

# Get current network
sage_rpc get_network '{}'

# Switch to testnet
sage_rpc set_network '{"name": "testnet11"}'

# Enable delta sync
sage_rpc set_delta_sync '{"delta_sync": true}'

# Set custom change address
sage_rpc set_change_address '{
  "fingerprint": 1234567890,
  "change_address": "xch1mychange..."
}'
```

## Network Override

Per-wallet network override for multi-network setups:

```bash
# Use testnet for specific wallet
sage_rpc set_network_override '{
  "fingerprint": 1234567890,
  "name": "testnet11"
}'

# Reset to default
sage_rpc set_network_override '{
  "fingerprint": 1234567890,
  "name": null
}'
```

## Notes

- Delta sync is faster but may miss some edge cases
- Target peers controls how many connections to maintain
- Network override allows testing without switching global network
