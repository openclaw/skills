---
name: slopesniper
description: Trade Solana tokens via Jupiter DEX with auto-execution and safety limits
metadata: {"moltbot":{"requires":{"bins":["slopesniper"]},"emoji":"🎯","homepage":"https://github.com/BAGWATCHER/SlopeSniper","install":[{"id":"uv-install","kind":"uv","package":"slopesniper-mcp","from":"git+https://github.com/BAGWATCHER/SlopeSniper.git#subdirectory=mcp-extension","bins":["slopesniper"],"label":"Install SlopeSniper via uv"}]},"clawdbot":{"requires":{"bins":["slopesniper"]},"emoji":"🎯","homepage":"https://github.com/BAGWATCHER/SlopeSniper","install":[{"id":"uv-install","kind":"uv","package":"slopesniper-mcp","from":"git+https://github.com/BAGWATCHER/SlopeSniper.git#subdirectory=mcp-extension","bins":["slopesniper"],"label":"Install SlopeSniper via uv"}]}}
user-invocable: true
homepage: https://github.com/BAGWATCHER/SlopeSniper
---

# SlopeSniper - Solana Trading Assistant

Trade Solana meme coins and tokens using natural language. Just tell me what you want to do.

## Examples

| You say | What happens |
|---------|--------------|
| "Check my status" | Shows wallet balance, holdings, and strategy |
| "Show my wallet" | Lists all token holdings with values |
| "Buy $25 of BONK" | Purchases BONK tokens |
| "Sell half my WIF" | Sells 50% of WIF position |
| "Sell all my POPCAT" | Exits entire position |
| "What's my PnL?" | Shows realized + unrealized profit/loss |
| "Show trade history" | Lists recent trades |
| "What's pumping?" | Scans for opportunities |
| "Is POPCAT safe?" | Runs rugcheck analysis |
| "Set aggressive mode" | Changes trading strategy |
| "Export my key" | Shows private key for backup |
| "Set a target to sell BONK at $1B mcap" | Creates auto-sell target |
| "List my targets" | Shows active sell targets |
| "Start the daemon" | Begins background monitoring |

## Important: Always Fetch Fresh Data

**CRITICAL:** When asked about prices, positions, or market data:
- **ALWAYS run the command** - Never rely on cached conversation data
- Crypto markets move fast - data older than 30 seconds is stale
- Run `slopesniper price MINT` or `slopesniper wallet` every time

**Example:**
```
User: "How's my Peyote position?"
BAD:  Use price from 30 minutes ago in conversation history
GOOD: Run `slopesniper wallet` to get current value
```

This ensures users always see accurate, real-time information.

## Getting Started

### New Users (Recommended)
```bash
slopesniper setup
```
Interactive setup with confirmation - guides you through wallet creation and ensures you save your private key.

### Quick Start
1. **Say "check my status"** - A wallet will be auto-generated on first run
2. **Save your private key** - It's shown once, save it securely!
3. **Fund your wallet** - Send SOL to the displayed address
4. **Start trading!** Just describe what you want in plain English

### Import Existing Wallet
```bash
slopesniper setup --import-key YOUR_PRIVATE_KEY
```

### Optional: Faster API
Set your own Jupiter API key for 10x better performance:
```bash
slopesniper config --set-jupiter-key YOUR_KEY
```
Get a free key at: https://station.jup.ag/docs/apis/ultra-api

## Performance Tips

### Multiple Positions (10+ tokens)

If you hold 10 or more different tokens, wallet balance checks may be slow due to Jupiter API rate limits.

**Symptoms:**
- `slopesniper wallet` takes 30+ seconds
- Retry messages in logs
- API timeout errors

**Solutions:**

1. **Get your own Jupiter API key** (Recommended):
   ```bash
   slopesniper config --set-jupiter-key YOUR_KEY
   ```
   Free keys at: https://station.jup.ag/docs/apis/ultra-api
   - 10x higher rate limits
   - Significantly faster for portfolios with many tokens

2. **Use custom RPC endpoint**:
   ```bash
   slopesniper config --set-rpc helius YOUR_KEY
   ```
   Reduces load on default public RPC

3. **Limit scanning**:
   - Avoid frequent `wallet` checks if not needed
   - Use position-specific commands when possible

## Trading Strategies

| Strategy | Max Trade | Auto-Execute | Safety Checks |
|----------|-----------|--------------|---------------|
| Conservative | $25 | Under $10 | Required |
| Balanced | $100 | Under $25 | Required |
| Aggressive | $500 | Under $50 | Optional |
| Degen | $1000 | Under $100 | None |

Say "set conservative mode" or "use aggressive strategy" to change.

## How It Works

```
You: "Buy $20 of BONK"
     ↓
[1] Resolve BONK → mint address
[2] Check rugcheck score
[3] Get Jupiter quote
[4] Auto-execute (under threshold)
     ↓
Result: "Bought 1.2M BONK for $20. Tx: solscan.io/tx/..."
```

For trades above your auto-execute threshold, you'll be asked to confirm first.

## Available Commands

### Trading
- `buy $X of TOKEN` - Purchase tokens
- `sell $X of TOKEN` - Sell tokens
- `sell X% of TOKEN` - Sell percentage of holdings
- `sell all TOKEN` - Exit entire position

### Account & Wallet
- `check status` / `am I ready?` - Full status with holdings
- `show wallet` / `my holdings` - View all token balances
- `export key` / `backup wallet` - Show private key for backup
- `what's my PnL?` - Profit/loss summary
- `trade history` - Recent trades

### Information
- `price of TOKEN` - Current price (symbol or mint)
- `search TOKEN` - Find token by name (returns mint addresses)
- `resolve TOKEN` - Get mint address from symbol
- `check TOKEN` / `is TOKEN safe?` - Safety analysis (symbol or mint)

### Strategy
- `set MODE strategy` - Change trading mode
- `what's my strategy?` - View current limits

### Scanning
- `what's trending?` - Find hot tokens
- `scan for opportunities` - Look for trades

### Auto-Sell Targets (v0.3.0+)
- `set target for TOKEN at $X mcap` - Auto-sell when market cap reached
- `set target for TOKEN at $X price` - Auto-sell at price target
- `set 100% gain target for TOKEN` - Auto-sell on percentage gain
- `set 20% trailing stop for TOKEN` - Trailing stop loss
- `list my targets` - View active targets
- `cancel target ID` - Remove a target
- `start the daemon` - Background monitoring
- `stop the daemon` - Stop background monitoring

## CLI Commands

Use the `slopesniper` CLI for direct execution:

```bash
# Wallet Setup (recommended for new users)
slopesniper setup               # Interactive wallet creation with confirmation
slopesniper setup --import-key KEY  # Import existing private key

# Account & Wallet
slopesniper status              # Full status: wallet, holdings, strategy, config
slopesniper wallet              # Show wallet address and all token holdings
slopesniper export              # Export private key for backup/recovery
slopesniper pnl                 # Show portfolio profit/loss
slopesniper pnl init            # Set baseline snapshot for tracking
slopesniper pnl stats           # Trading statistics (win rate, avg gain/loss)
slopesniper pnl positions       # Detailed position breakdown
slopesniper pnl export          # Export trade history as JSON
slopesniper pnl export --format csv   # Export as CSV
slopesniper pnl reset           # Reset PnL baseline
slopesniper history             # Show recent trade history
slopesniper history 50          # Show last 50 trades

# Trading
slopesniper price SOL           # Get token price
slopesniper price BONK          # Get meme coin price
slopesniper buy BONK 25         # Buy $25 of BONK
slopesniper sell WIF 50         # Sell $50 of WIF
slopesniper sell WIF all        # Sell entire WIF position

# Token Discovery
slopesniper search "dog"        # Search for tokens by name
slopesniper check POPCAT        # Safety check (rugcheck analysis)
slopesniper resolve BONK        # Get mint address from symbol
slopesniper scan                # Scan for all opportunities
slopesniper scan trending       # Scan trending tokens
slopesniper scan new            # Scan new pairs
slopesniper scan graduated      # Scan pump.fun graduates
slopesniper scan pumping        # Scan tokens with price spikes

# Strategy & Config
slopesniper strategy            # View current strategy
slopesniper strategy aggressive # Set aggressive mode
slopesniper config              # View current configuration
slopesniper config --set-jupiter-key KEY  # Set custom API key (10x faster!)
slopesniper config --set-rpc mainnet URL  # Set custom RPC endpoint

# Auto-Sell Targets
slopesniper target add BONK --mcap 1000000000 --sell all   # Sell all at $1B mcap
slopesniper target add WIF --price 5.00 --sell 50%         # Sell half at $5
slopesniper target add POPCAT --pct-gain 100 --sell all    # Sell on 2x
slopesniper target add TOKEN --trailing 20 --sell all      # 20% trailing stop
slopesniper target list         # List active targets
slopesniper target list --all   # List all targets (including triggered)
slopesniper target remove ID    # Cancel a target

# Watch Mode (foreground)
slopesniper watch BONK --mcap 1000000000 --sell all        # Watch until target hit

# Daemon (background monitoring)
slopesniper daemon start        # Start background target monitoring
slopesniper daemon start --interval 15  # Custom poll interval (seconds)
slopesniper daemon stop         # Stop daemon
slopesniper daemon status       # Check if daemon is running

# Updates
slopesniper version             # Show current version
slopesniper version --check     # Check for updates
slopesniper update              # Update to latest version (shows changelog)
```

All commands output JSON with mint addresses included for easy chaining.

## Security

- **Use a dedicated wallet** - Only fund with amounts you're willing to lose
- **Start with conservative mode** - Get comfortable before increasing limits
- **Rugcheck integration** - Automatic scam token detection
- **Two-step confirmation** - Large trades require explicit approval
- **Encrypted storage** - Private keys encrypted at rest, machine-bound

### ⚠️ BACKUP YOUR PRIVATE KEY

Your private key is shown **once** at wallet creation. Retrieve it anytime with:
```bash
slopesniper export
```

**Back it up OUTSIDE this system:**
- Password manager (1Password, Bitwarden)
- Encrypted USB drive
- Paper backup in secure location

**The wallet file is machine-bound. If your computer dies without a backup, your funds are lost forever.**

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLANA_PRIVATE_KEY` | No | Import existing wallet (auto-generates if not set) |
| `SOLANA_RPC_URL` | No | Custom RPC (defaults to public mainnet) |
| `JUPITER_API_KEY` | No | Your own key for 10x better performance |

**Note:** Wallet and API keys are stored encrypted in `~/.slopesniper/`

## Troubleshooting

### Common Issues

| Error | Fix |
|-------|-----|
| 401 Unauthorized | `slopesniper config --clear jupiter-key` |
| Trade failed (slippage) | `slopesniper strategy --slippage 300` |
| Wallet mismatch | `slopesniper health` to check sync |
| Wallet reverts to old address | `slopesniper health --diagnose` then restore from backup |
| Slow transactions | Configure custom RPC (see below) |

### Health Check

Run a full system health check:
```bash
slopesniper health
```

For comprehensive diagnostics (wallet integrity, machine key status, backups):
```bash
slopesniper health --diagnose
```

This shows:
- Wallet source (environment vs local file)
- Sync status and mismatch warnings
- API key configuration
- RPC provider status
- (with --diagnose) Machine key integrity, backup availability, specific issues and recommendations

### Wallet Recovery

If your wallet keeps reverting or you need to restore from backup:

1. **List available backups:**
   ```bash
   slopesniper export --list-backups
   ```

2. **Restore from a backup:**
   ```bash
   slopesniper restore TIMESTAMP
   ```
   (Replace TIMESTAMP with value from list-backups, e.g., `20240127_103045`)

3. **If backups can't be decrypted** (different machine):
   - Re-import your private key: `slopesniper setup --import-key YOUR_KEY`
   - Check address files in `~/.slopesniper/wallet_backups/*.address` for reference

### Reporting Issues

If you encounter persistent errors:
1. Run `slopesniper health --diagnose` and note the output
2. Create an issue at: https://github.com/BAGWATCHER/SlopeSniper/issues
3. Include: error message, health output, steps to reproduce

**For the bot:** When errors occur repeatedly, create a GitHub issue automatically using this priority:

1. **GitHub MCP tool** (preferred): Use `mcp__github__create_issue` with:
   - `owner`: "BAGWATCHER"
   - `repo`: "SlopeSniper"
   - `title`: Brief description of the issue
   - `body`: Full details including error, steps to reproduce, environment
   - `labels`: ["bug"] or ["enhancement"]

2. **gh CLI** (fallback): If MCP unavailable, use `gh issue create --repo BAGWATCHER/SlopeSniper`

3. **Manual** (last resort): Create local markdown file and provide the GitHub issues URL

Always include in issue body:
- Error message or behavior observed
- Steps to reproduce
- Environment (Moltbot/Claude Code version)
- Output from `slopesniper health --diagnose` if relevant

## Support

- GitHub: https://github.com/BAGWATCHER/SlopeSniper
- Issues: https://github.com/BAGWATCHER/SlopeSniper/issues
