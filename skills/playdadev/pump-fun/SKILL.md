---
name: pump-fun
description: Buy, sell, and launch tokens on Pump.fun using the PumpPortal API
homepage: https://pump.fun
user-invocable: true
metadata: {"moltbot":{"requires":{"env":["SOLANA_PRIVATE_KEY"]},"primaryEnv":"SOLANA_PRIVATE_KEY"}}
---

# Pump.fun Trading Skill

This skill enables trading and launching tokens on Pump.fun through the PumpPortal API.

## Commands

### Buy Tokens
Buy tokens on Pump.fun by specifying the token mint address and amount.

**Usage:** `/pump-buy <mint_address> <amount_sol> [slippage]`

**Examples:**
- `/pump-buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.1` - Buy 0.1 SOL worth of tokens
- `/pump-buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.5 15` - Buy with 15% slippage

### Sell Tokens
Sell tokens on Pump.fun by specifying the token mint address and amount.

**Usage:** `/pump-sell <mint_address> <amount|percentage> [slippage]`

**Examples:**
- `/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 1000000` - Sell 1,000,000 tokens
- `/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 100%` - Sell all tokens
- `/pump-sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 50% 10` - Sell 50% with 10% slippage

### Launch Token
Create and launch a new token on Pump.fun.

**Usage:** `/pump-launch <name> <symbol> <description> [dev_buy_sol]`

**Examples:**
- `/pump-launch "My Token" MTK "A revolutionary token" 1` - Launch with 1 SOL dev buy
- `/pump-launch "Cool Coin" COOL "The coolest coin ever"` - Launch with default dev buy

## Configuration

### Required Environment Variables
- `SOLANA_PRIVATE_KEY` - Your Solana wallet private key (base58 encoded)

### Optional Environment Variables
- `SOLANA_RPC_URL` - Custom RPC endpoint (defaults to public mainnet)
- `PUMP_PRIORITY_FEE` - Priority fee in SOL (default: 0.0005)
- `PUMP_DEFAULT_SLIPPAGE` - Default slippage percentage (default: 10)

## Setup

1. Install dependencies:
   ```bash
   cd {baseDir}
   npm install
   ```

2. Set your environment variables:
   ```bash
   export SOLANA_PRIVATE_KEY="your-base58-private-key"
   ```

3. (Optional) Configure custom RPC:
   ```bash
   export SOLANA_RPC_URL="https://your-rpc-endpoint.com"
   ```

## Security Notes

- Never share your private key
- Use a dedicated trading wallet with limited funds
- Start with small amounts to test
- The skill uses the Local Transaction API for maximum security (transactions are signed locally)

## Fees

- PumpPortal charges a 0.5% fee per trade
- Standard Solana network fees apply
- Priority fees are configurable

## Supported Pools

The skill automatically selects the best pool, but supports:
- `pump` - Pump.fun bonding curve
- `raydium` - Raydium AMM (for graduated tokens)
- `pump-amm` - Pump.fun AMM
- `auto` - Automatic pool selection (default)
