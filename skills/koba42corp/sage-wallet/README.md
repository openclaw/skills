<p align="center">
  <h1 align="center">🌿 Sage Wallet</h1>
  <p align="center">
    <strong>Complete RPC interface to the Sage Chia blockchain wallet</strong>
  </p>
  <p align="center">
    <em>112 endpoints across 12 domain skills for XCH, CATs, NFTs, DIDs, Offers, and more</em>
  </p>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.chia.net/">
    <img src="https://img.shields.io/badge/Blockchain-Chia-3AAC59.svg" alt="Chia Blockchain">
  </a>
  <a href="https://github.com/xch-dev/sage">
    <img src="https://img.shields.io/badge/Wallet-Sage-blue.svg" alt="Sage Wallet">
  </a>
  <a href="https://clawd.bot">
    <img src="https://img.shields.io/badge/Framework-Clawdbot-orange.svg" alt="Built for Clawdbot">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Endpoints-112-brightgreen.svg" alt="112 Endpoints">
  <img src="https://img.shields.io/badge/Sub--Skills-12-blue.svg" alt="12 Sub-Skills">
  <img src="https://img.shields.io/badge/Platforms-Mac%20%7C%20Linux%20%7C%20Windows-purple.svg" alt="Cross Platform">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
</p>

---

## 🎯 Overview

Full RPC integration with [Sage Wallet](https://github.com/xch-dev/sage) for Chia blockchain operations. Send XCH, manage CAT tokens, mint NFTs, create offers, and more — all through natural language or slash commands.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 💰 **XCH Transactions**
- Send to single or multiple addresses
- Combine and split coins
- Auto-combine dust
- Clawback support

### 🪙 **CAT Tokens**
- Issue new tokens
- Send and receive CATs
- Track balances
- Auto-combine CAT coins

### 🖼️ **NFTs**
- Mint single or bulk NFTs
- Transfer ownership
- Manage collections
- Add URIs and metadata

</td>
<td width="50%">

### 🆔 **DIDs**
- Create identities
- Transfer DIDs
- Link NFTs to DIDs
- Provenance tracking

### 🤝 **Offers**
- Create P2P offers
- Accept and combine offers
- Cancel on-chain
- View offer details

### ⚙️ **System**
- Sync status monitoring
- Database maintenance
- Network peer management
- WalletConnect integration

</td>
</tr>
</table>

---

## 📋 Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Sage Wallet** | Latest | Running with RPC enabled |
| **Bash** | 4.0+ | Shell scripting |
| **curl** | Any | HTTP client |
| **jq** | Any | JSON processing |
| **Clawdbot** | Latest | Agent framework |

---

## 🖥️ Platform Support

| Platform | Default Cert Path |
|----------|-------------------|
| **macOS** | `~/Library/Application Support/com.rigidnetwork.sage/ssl/wallet.crt` |
| **Linux** | `~/.local/share/sage/ssl/wallet.crt` |
| **Windows** | `%APPDATA%\com.rigidnetwork.sage\ssl\wallet.crt` |

Platform auto-detected, or set manually with `/sage config platform`.

---

## 🚀 Installation

### Via ClawdHub (Recommended)

```bash
clawdhub install sage-wallet
```

### Manual Installation

1. Download and extract to `~/clawd/skills/sage-wallet/`
2. Make scripts executable:
   ```bash
   chmod +x ~/clawd/skills/sage-wallet/scripts/*.sh
   ```

---

## 🎬 Quick Start

### Step 1️⃣: Verify Sage is Running

Ensure Sage Wallet is running with RPC enabled (default port 9257).

### Step 2️⃣: Test Connection

```
/sage status
```

This auto-detects your platform, finds certificates, and tests the connection.

### Step 3️⃣: Login to Wallet

```
/sage login 1234567890
```

Replace with your wallet fingerprint.

### Step 4️⃣: Start Using

```
/sage balance
/sage nfts
/sage send xch xch1... 1.5
```

---

## 💬 Commands Reference

### ⚙️ Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `/sage status` | Show config & test connection | `/sage status` |
| `/sage config` | Display settings | `/sage config` |
| `/sage config platform <p>` | Set platform | `/sage config platform mac` |
| `/sage config rpc <url>` | Set RPC URL | `/sage config rpc https://192.168.1.50:9257` |
| `/sage config cert <path>` | Set cert path | `/sage config cert /path/to/wallet.crt` |
| `/sage config key <path>` | Set key path | `/sage config key /path/to/wallet.key` |
| `/sage config fingerprint <fp>` | Set default fingerprint | `/sage config fingerprint 1234567890` |
| `/sage config autologin <on/off>` | Toggle auto-login | `/sage config autologin on` |
| `/sage config reset` | Reset to defaults | `/sage config reset` |

### 🔐 Authentication

| Command | Description |
|---------|-------------|
| `/sage login <fingerprint>` | Login to wallet |
| `/sage logout` | End session |
| `/sage keys` | List wallet keys |
| `/sage mnemonic generate` | Generate new mnemonic |

### 💰 XCH Transactions

| Command | Description |
|---------|-------------|
| `/sage balance` | Check XCH balance |
| `/sage send xch <addr> <amount>` | Send XCH |
| `/sage send xch <addr> <amount> --fee 0.0001` | Send with fee |
| `/sage combine` | Auto-combine dust |
| `/sage split <coin_id> <count>` | Split coin |

### 🪙 CAT Tokens

| Command | Description |
|---------|-------------|
| `/sage cats` | List CAT tokens |
| `/sage send cat <asset_id> <addr> <amount>` | Send CAT |
| `/sage issue cat <name> <ticker> <supply>` | Issue new CAT |

### 🖼️ NFTs

| Command | Description |
|---------|-------------|
| `/sage nfts` | List NFTs |
| `/sage nft <nft_id>` | Get NFT details |
| `/sage collections` | List collections |
| `/sage mint nft --did <did> --data <uri>` | Mint NFT |
| `/sage transfer nft <nft_id> <address>` | Transfer NFT |

### 🆔 DIDs

| Command | Description |
|---------|-------------|
| `/sage dids` | List DIDs |
| `/sage create did <name>` | Create DID |
| `/sage transfer did <did_id> <address>` | Transfer DID |

### 🤝 Offers

| Command | Description |
|---------|-------------|
| `/sage offers` | List offers |
| `/sage offer view <offer_string>` | View offer details |
| `/sage offer make --request <xch:1> --offer <cat:1000>` | Create offer |
| `/sage offer take <offer_string>` | Accept offer |
| `/sage offer cancel <offer_id>` | Cancel on-chain |

### 📊 System

| Command | Description |
|---------|-------------|
| `/sage sync` | Sync status |
| `/sage version` | Wallet version |
| `/sage peers` | Connected peers |
| `/sage network` | Current network |
| `/sage pending` | Pending transactions |

### 🔧 Global Options

All commands accept optional overrides:

```
--fingerprint <fp>    Use specific wallet
--rpc <url>           Override RPC URL
--cert <path>         Override cert path
--key <path>          Override key path
```

---

## 📁 Skill Structure

```
sage-wallet/
├── SKILL.md                    # Master skill (orchestration)
├── README.md                   # This file
├── references/
│   └── endpoints.md            # All 112 endpoints reference
├── scripts/
│   ├── sage-config.sh          # Configuration management
│   ├── sage-rpc.sh             # mTLS RPC caller
│   ├── test-config.sh          # Config tests
│   ├── test-rpc.sh             # RPC tests
│   └── test-integration.sh     # Full integration tests
└── sub-skills/
    ├── sage-auth/              # Authentication & keys
    ├── sage-xch/               # XCH transactions
    ├── sage-cat/               # CAT tokens
    ├── sage-nft/               # NFTs
    ├── sage-did/               # DIDs
    ├── sage-offers/            # Offers
    ├── sage-options/           # Options protocol
    ├── sage-coins/             # Coins & addresses
    ├── sage-txn/               # Transaction signing
    ├── sage-network/           # Network & peers
    ├── sage-system/            # System & sync
    └── sage-walletconnect/     # WalletConnect
```

---

## 🔌 Sub-Skills

Each domain has a dedicated sub-skill with full endpoint documentation:

| Sub-Skill | Endpoints | Description |
|-----------|-----------|-------------|
| **sage-auth** | 16 | Login, logout, keys, mnemonics, themes |
| **sage-xch** | 7 | Send, bulk send, combine, split, clawback |
| **sage-cat** | 9 | List, send, issue, combine CAT tokens |
| **sage-nft** | 14 | Mint, transfer, collections, URIs |
| **sage-did** | 6 | Create, transfer, normalize DIDs |
| **sage-offers** | 11 | Create, take, view, cancel offers |
| **sage-options** | 6 | Mint, exercise, transfer options |
| **sage-coins** | 8 | List coins, addresses, derivations |
| **sage-txn** | 6 | Sign, submit, pending transactions |
| **sage-network** | 12 | Peers, network settings, sync config |
| **sage-system** | 4 | Version, sync status, database |
| **sage-walletconnect** | 5 | dApp connectivity, message signing |

**Total: 112 endpoints**

---

## 🧪 Testing

### Run Config Tests

```bash
./scripts/test-config.sh
```

### Run RPC Tests (Dry Mode)

```bash
./scripts/test-rpc.sh
```

### Run RPC Tests (Live)

```bash
./scripts/test-rpc.sh --live
```

### Full Integration Test

```bash
./scripts/test-integration.sh --fingerprint 1234567890
```

---

## ⚙️ Configuration File

Location: `~/.config/sage-wallet/config.json`

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

| Field | Type | Description |
|-------|------|-------------|
| `platform` | string | `"auto"`, `"mac"`, `"linux"`, or `"windows"` |
| `rpc_url` | string | Sage RPC endpoint |
| `cert_path` | string/null | Custom cert path (null = platform default) |
| `key_path` | string/null | Custom key path (null = platform default) |
| `fingerprint` | number/null | Default wallet fingerprint |
| `auto_login` | boolean | Auto-login on first RPC call |

---

## 💱 Amount Formatting

Sage uses **mojos** (smallest unit). Conversions:

| XCH | Mojos |
|-----|-------|
| 1 XCH | `1000000000000` |
| 0.1 XCH | `100000000000` |
| 0.001 XCH | `1000000000` |
| 0.000001 XCH | `1000000` |

CAT amounts are in the token's smallest unit (no decimals in RPC).

---

## 🔧 Troubleshooting

<details>
<summary><b>❌ "Certificate not found"</b></summary>

**Solution:**
1. Verify Sage is installed and has been run at least once
2. Check platform detection: `/sage config`
3. Set path manually:
   ```
   /sage config cert /path/to/wallet.crt
   /sage config key /path/to/wallet.key
   ```
</details>

<details>
<summary><b>❌ "Connection refused"</b></summary>

**Solution:**
1. Ensure Sage wallet is running
2. Check RPC is enabled in Sage settings
3. Verify port 9257 is accessible:
   ```bash
   curl -k https://127.0.0.1:9257/get_version
   ```
4. Check custom RPC URL if set: `/sage config`
</details>

<details>
<summary><b>❌ "Unauthorized" error</b></summary>

**Solution:**
1. Sage uses mutual TLS — both cert and key required
2. Ensure cert/key files are readable
3. Verify cert matches the Sage installation
4. Try regenerating certs in Sage settings
</details>

<details>
<summary><b>❌ "Not logged in"</b></summary>

**Solution:**
1. Login with fingerprint: `/sage login 1234567890`
2. Or set default fingerprint:
   ```
   /sage config fingerprint 1234567890
   /sage config autologin on
   ```
</details>

<details>
<summary><b>❌ Wrong platform detected</b></summary>

**Solution:**
```
/sage config platform linux
```
Options: `auto`, `mac`, `linux`, `windows`
</details>

---

## 🔐 Security Notes

> **Important:** This skill interacts with real cryptocurrency wallets.

### ✅ Best Practices

- Never share your mnemonic or wallet.key file
- Use testnet for development and testing
- Verify transaction details before submitting
- Keep Sage wallet software updated
- Use clawback for large transfers to new addresses

### 🔒 What This Skill Does

- Reads certificates from your local Sage installation
- Makes authenticated RPC calls to your local wallet
- Does **not** store or transmit mnemonics
- Does **not** access remote wallets (unless you configure a remote RPC)

---

## 📊 Use Cases

### 💼 **Portfolio Management**
Check balances, track NFTs, and monitor transactions across wallets.

### 🤖 **Automated Trading**
Create and manage offers programmatically through natural language.

### 🎨 **NFT Operations**
Bulk mint, transfer, and organize NFT collections.

### 🔄 **Token Distribution**
Bulk send CAT tokens or XCH to multiple addresses.

### 📈 **Wallet Monitoring**
Track sync status, pending transactions, and network health.

---

## 🗺️ Roadmap

### ✅ Completed (v1.0.0)
- [x] All 112 RPC endpoints mapped
- [x] 12 domain sub-skills
- [x] Cross-platform support (Mac/Linux/Windows)
- [x] Configuration management
- [x] Test suites
- [x] Comprehensive documentation

### 🚧 Planned
- [ ] Transaction builder with confirmation prompts
- [ ] Offer marketplace integration
- [ ] Price feed integration (XCH/USD)
- [ ] Portfolio analytics
- [ ] Multi-wallet dashboard
- [ ] Scheduled transactions
- [ ] Webhook notifications

---

## 🤝 Contributing

Contributions welcome! 

- **Bug Reports:** Open an issue with reproduction steps
- **Feature Requests:** Describe the use case
- **Pull Requests:** Fork, branch, test, submit

---

## 📄 License

MIT License — Koba42 Corp

---

## 🙏 Credits

Built with ❤️ by **Koba42 Corp**

### Powered By:
- 🌿 [Sage Wallet](https://github.com/xch-dev/sage) - Chia wallet
- 🌱 [Chia Blockchain](https://www.chia.net/) - Green cryptocurrency
- 🦾 [Clawdbot](https://clawd.bot) - Agent framework
- 🔧 [curl](https://curl.se/) - HTTP client
- 📋 [jq](https://jqlang.github.io/jq/) - JSON processor

### Resources:
- [Sage Wallet GitHub](https://github.com/xch-dev/sage)
- [Chia Developer Documentation](https://docs.chia.net/)
- [Clawdbot Documentation](https://docs.clawd.bot)
- [ClawdHub](https://clawdhub.com)

---

## 📬 Support

- 💬 **Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- 📖 **Docs:** [docs.clawd.bot](https://docs.clawd.bot)
- 🐛 **Issues:** GitHub Issues

---

<p align="center">
  <strong>⭐ Star us on GitHub if this skill helped you!</strong>
</p>

<p align="center">
  <em>"The Chia blockchain: where sustainability meets innovation."</em>
</p>

<p align="center">
  <sub>Version 1.0.0 | January 2026</sub>
</p>
