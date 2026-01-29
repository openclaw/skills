# Pump.fun Skill for MoltBot

An open-source MoltBot skill that enables buying, selling, and launching tokens on [Pump.fun](https://pump.fun) using the [PumpPortal](https://pumpportal.fun) Local Transaction API.

## Features

- **Buy Tokens**: Purchase tokens using SOL with configurable slippage
- **Sell Tokens**: Sell tokens by amount or percentage (e.g., "50%", "100%")
- **Launch Tokens**: Create and launch new tokens with custom metadata
- **Local Signing**: All transactions are signed locally for maximum security
- **Multi-Pool Support**: Automatic pool selection (pump, raydium, pump-amm, etc.)

## Installation

### Prerequisites

- [Node.js](https://nodejs.org/) v22 or higher
- [MoltBot](https://github.com/moltbot/moltbot) installed and configured
- A Solana wallet with SOL for trading

### Install Dependencies

```bash
cd pump-fun-skill
npm install
npm run build
```

### Add to MoltBot

Copy the skill to your MoltBot skills directory:

```bash
# For managed skills (globally available)
cp -r pump-fun-skill ~/.clawdbot/skills/

# Or for workspace skills (project-specific)
cp -r pump-fun-skill /path/to/your/workspace/skills/
```

## Configuration

### Required Environment Variables

```bash
export SOLANA_PRIVATE_KEY="your-base58-encoded-private-key"
```

### Optional Environment Variables

```bash
# Custom RPC endpoint (recommended for production)
export SOLANA_RPC_URL="https://your-rpc-endpoint.com"

# Priority fee in SOL (default: 0.0005)
export PUMP_PRIORITY_FEE="0.001"

# Default slippage percentage (default: 10)
export PUMP_DEFAULT_SLIPPAGE="15"
```

### MoltBot Configuration

Add to your `~/.clawdbot/moltbot.json`:

```json5
{
  skills: {
    entries: {
      "pump-fun": {
        enabled: true,
        env: {
          SOLANA_PRIVATE_KEY: "your-private-key",
          SOLANA_RPC_URL: "https://your-rpc-endpoint.com"
        }
      }
    }
  }
}
```

## Usage

### Via MoltBot Chat Commands

```
# Buy tokens
/pump-buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.1

# Buy with custom slippage
/pump-buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.5 15

# Sell specific amount
/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 1000000

# Sell percentage of holdings
/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 50%

# Sell all tokens
/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 100%

# Launch a new token
/pump-launch "My Token" MTK "An amazing new token" 1
```

### Via CLI

```bash
# Build first
npm run build

# Buy tokens
node dist/cli.js buy <mint> <amount_sol> [slippage]

# Sell tokens
node dist/cli.js sell <mint> <amount|percentage> [slippage]

# Launch token
node dist/cli.js launch <name> <symbol> <description> [dev_buy_sol]
```

### Programmatic Usage

```typescript
import { buyTokens, sellTokens, launchToken } from 'pump-fun-skill';

// Buy 0.1 SOL worth of tokens
const buyResult = await buyTokens(
  '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
  0.1,
  { slippage: 15 }
);

if (buyResult.success) {
  console.log('Transaction:', buyResult.data.explorerUrl);
}

// Sell 50% of your tokens
const sellResult = await sellTokens(
  '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
  '50%'
);

// Launch a new token
const launchResult = await launchToken(
  'My Token',
  'MTK',
  'The best token on Solana',
  {
    devBuyAmountSol: 1,
    twitter: 'https://twitter.com/mytoken',
    website: 'https://mytoken.com'
  }
);

if (launchResult.success) {
  console.log('Token launched:', launchResult.data.pumpFunUrl);
}
```

## API Reference

### `buyTokens(mint, amountSol, options?)`

Buy tokens on Pump.fun.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mint` | `string` | Token contract address |
| `amountSol` | `number` | Amount of SOL to spend |
| `options.slippage` | `number` | Slippage tolerance (default: 10%) |
| `options.priorityFee` | `number` | Priority fee in SOL |
| `options.pool` | `string` | Pool to use (auto, pump, raydium, etc.) |

### `sellTokens(mint, amount, options?)`

Sell tokens on Pump.fun.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mint` | `string` | Token contract address |
| `amount` | `number \| string` | Token amount or percentage (e.g., "50%") |
| `options.slippage` | `number` | Slippage tolerance (default: 10%) |
| `options.priorityFee` | `number` | Priority fee in SOL |
| `options.pool` | `string` | Pool to use (auto, pump, raydium, etc.) |

### `launchToken(name, symbol, description, options?)`

Create and launch a new token.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `string` | Token name (max 32 chars) |
| `symbol` | `string` | Token symbol (max 10 chars) |
| `description` | `string` | Token description |
| `options.devBuyAmountSol` | `number` | Initial dev buy in SOL |
| `options.imagePath` | `string` | Local path to token image |
| `options.imageUrl` | `string` | URL to token image |
| `options.twitter` | `string` | Twitter profile URL |
| `options.telegram` | `string` | Telegram group URL |
| `options.website` | `string` | Website URL |

## Security Considerations

1. **Private Key Safety**: Never share your private key. Use a dedicated trading wallet.
2. **Local Signing**: All transactions are signed locally - your private key is never sent to any server.
3. **Test First**: Always test with small amounts before trading larger sums.
4. **RPC Endpoint**: Consider using a private RPC endpoint for better reliability and privacy.

## Fees

- **PumpPortal API**: 0.5% per trade
- **Solana Network**: Standard transaction fees
- **Priority Fees**: Configurable (default: 0.0005 SOL)

## Supported Pools

| Pool | Description |
|------|-------------|
| `pump` | Pump.fun bonding curve |
| `raydium` | Raydium AMM (graduated tokens) |
| `pump-amm` | Pump.fun AMM |
| `raydium-cpmm` | Raydium CPMM |
| `bonk` | Bonk launchpad |
| `auto` | Automatic selection (recommended) |

## Troubleshooting

### "SOLANA_PRIVATE_KEY environment variable is required"

Set your private key:
```bash
export SOLANA_PRIVATE_KEY="your-base58-private-key"
```

### "Invalid private key format"

Ensure your private key is base58 encoded (the format used by Phantom and other Solana wallets).

### "Transaction failed: insufficient funds"

Make sure your wallet has enough SOL for the trade plus transaction fees.

### "Slippage exceeded"

Increase the slippage parameter or try again when the market is less volatile.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This software is provided as-is. Trading cryptocurrencies involves significant risk. Always do your own research and never trade more than you can afford to lose.

## Credits

- [MoltBot](https://github.com/moltbot/moltbot) - The AI assistant platform
- [PumpPortal](https://pumpportal.fun) - The Pump.fun API provider
- [Pump.fun](https://pump.fun) - The token launchpad
