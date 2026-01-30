---
name: sage-wallet
description: Interact with the Sage Chia blockchain wallet via RPC. Use for XCH transactions, CAT tokens, NFTs, DIDs, offers, options, coin management, and wallet configuration. Supports cross-platform setups (Mac/Linux/Windows) with configurable RPC endpoints and SSL certificates. Invoke with /sage commands or natural language like "send XCH", "check my NFTs", "create an offer", "mint a CAT token".
---

# Sage Wallet Skill

RPC interface to Sage wallet for Chia blockchain operations.

## Configuration

User settings stored in `{workspace}/config/sage-wallet.json`:

```json
{
  "platform": "auto",
  "rpc_url": "https://127.0.0.1:9257",
  "cert_path": null,
  "key_path": null,
  "fingerprint": null,
  "auto_login": false
}
```

### Platform Defaults

| Platform | Cert Path | Key Path |
|----------|-----------|----------|
| mac | `~/Library/Application Support/com.rigidnetwork.sage/ssl/wallet.crt` | `...wallet.key` |
| linux | `~/.local/share/sage/ssl/wallet.crt` | `...wallet.key` |
| windows | `%APPDATA%\com.rigidnetwork.sage\ssl\wallet.crt` | `...wallet.key` |

When `platform` is `"auto"`, detect via `uname -s`.

## Slash Commands

### Configuration

| Command | Action |
|---------|--------|
| `/sage status` | Show config and test connection |
| `/sage config` | Display current settings |
| `/sage config platform <auto\|mac\|linux\|windows>` | Set platform |
| `/sage config rpc <url>` | Set RPC URL |
| `/sage config cert <path>` | Set SSL cert path |
| `/sage config key <path>` | Set SSL key path |
| `/sage config fingerprint <fp>` | Set default wallet fingerprint |
| `/sage config autologin <on\|off>` | Toggle auto-login |
| `/sage config reset` | Reset to defaults |

### Operations

Route to appropriate sub-skill based on domain:

| Domain | Sub-Skill | Example Commands |
|--------|-----------|------------------|
| Auth & Keys | `sage-auth` | `/sage login`, `/sage logout`, `/sage keys` |
| XCH | `sage-xch` | `/sage send xch`, `/sage balance`, `/sage combine` |
| CAT Tokens | `sage-cat` | `/sage cats`, `/sage send cat`, `/sage issue cat` |
| NFTs | `sage-nft` | `/sage nfts`, `/sage mint nft`, `/sage transfer nft` |
| DIDs | `sage-did` | `/sage dids`, `/sage create did` |
| Offers | `sage-offers` | `/sage offers`, `/sage make offer`, `/sage take offer` |
| Options | `sage-options` | `/sage options`, `/sage mint option` |
| Coins | `sage-coins` | `/sage coins`, `/sage check address` |
| Transactions | `sage-txn` | `/sage pending`, `/sage submit` |
| Network | `sage-network` | `/sage peers`, `/sage network` |
| System | `sage-system` | `/sage sync`, `/sage version` |
| WalletConnect | `sage-walletconnect` | `/sage wc sign` |

### Global Parameters

All commands accept optional overrides:

- `--fingerprint <fp>` — Use specific wallet
- `--rpc <url>` — Override RPC URL
- `--cert <path>` — Override cert path
- `--key <path>` — Override key path

## Scripts

- `scripts/sage-config.sh` — Config management
- `scripts/sage-rpc.sh` — RPC caller with mTLS

### Making RPC Calls

```bash
# Source the RPC helper
source scripts/sage-rpc.sh

# Call an endpoint
sage_rpc "get_sync_status" '{}'
sage_rpc "send_xch" '{"address":"xch1...","amount":"1000000000000","fee":"100000000"}'
```

## Sub-Skills

Each sub-skill handles a specific domain. Load the appropriate one based on the operation:

| Sub-Skill | When to Load |
|-----------|--------------|
| [sage-auth](sub-skills/sage-auth/SKILL.md) | Login, logout, key management, mnemonics |
| [sage-xch](sub-skills/sage-xch/SKILL.md) | Send/receive XCH, combine, split coins |
| [sage-cat](sub-skills/sage-cat/SKILL.md) | CAT token operations |
| [sage-nft](sub-skills/sage-nft/SKILL.md) | NFT minting, transfers, collections |
| [sage-did](sub-skills/sage-did/SKILL.md) | DID creation and management |
| [sage-offers](sub-skills/sage-offers/SKILL.md) | Offer creation, acceptance, cancellation |
| [sage-options](sub-skills/sage-options/SKILL.md) | Options protocol operations |
| [sage-coins](sub-skills/sage-coins/SKILL.md) | Coin queries, address validation |
| [sage-txn](sub-skills/sage-txn/SKILL.md) | Transaction signing, submission |
| [sage-network](sub-skills/sage-network/SKILL.md) | Peer and network settings |
| [sage-system](sub-skills/sage-system/SKILL.md) | Sync status, version, database |
| [sage-walletconnect](sub-skills/sage-walletconnect/SKILL.md) | WalletConnect integration |

## First Run

On first invocation:

1. Check for config file; create if missing
2. Detect platform if set to `"auto"`
3. Verify cert/key files exist
4. If missing, prompt user to configure paths
5. Test connection with `GetVersion`

If certs not found, guide user:
```
Sage certificates not found. Configure with:
  /sage config cert /path/to/wallet.crt
  /sage config key /path/to/wallet.key
```

## Error Handling

RPC errors return HTTP status codes:
- `400` — Bad request (invalid params)
- `401` — Unauthorized (cert mismatch)
- `404` — Not found
- `500` — Internal error

Always check response for error field before processing data.

## Amount Formatting

Sage uses mojos (1 XCH = 1,000,000,000,000 mojos). The `Amount` type in requests/responses is a string representing mojos. Convert for display:

```
1 XCH = "1000000000000"
0.001 XCH = "1000000000"
```
