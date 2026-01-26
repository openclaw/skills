---
name: solana
description: Solana wallet operations - create wallets, check balances, send SOL/tokens, swap via Jupiter, launch tokens on Pump.fun
triggers:
  - solana
  - wallet
  - sol balance
  - send sol
  - send token
  - swap
  - jupiter
  - pumpfun
  - pump.fun
  - launch token
metadata:
  clawdbot:
    emoji: "◎"
    requires:
      env:
        - SOLANA_PRIVATE_KEY
        - JUPITER_API_KEY
    primaryEnv: SOLANA_PRIVATE_KEY
---

# Solana Wallet ◎

Solana wallet management and token operations for AI agents.

## Setup

```bash
pip install -r requirements.txt
```

## Initialize Wallet

First, create a new wallet and save the private key to your `.env` file:

```bash
python3 {baseDir}/scripts/initialize.py
```

This will:
- Generate a new Solana keypair
- Display the public key (wallet address)
- Save the private key in base58 format to `.env` as `SOLANA_PRIVATE_KEY`

**IMPORTANT**: After running initialize.py, export the private key to your environment:
```bash
export SOLANA_PRIVATE_KEY=$(grep SOLANA_PRIVATE_KEY .env | cut -d '=' -f2)
```

Or source the .env file:
```bash
source .env
```

## Wallet Operations

### Check SOL Balance
```bash
python3 {baseDir}/scripts/wallet.py balance
python3 {baseDir}/scripts/wallet.py balance <wallet_address>
```

### Check Token Balance
```bash
python3 {baseDir}/scripts/wallet.py token-balance <token_mint_address>
python3 {baseDir}/scripts/wallet.py token-balance <token_mint_address> --owner <wallet_address>
```

### Send SOL
```bash
python3 {baseDir}/scripts/wallet.py send <recipient_address> <amount_in_sol>
```

### Send SPL Token
```bash
python3 {baseDir}/scripts/wallet.py send-token <token_mint_address> <recipient_address> <amount>
```

### Get Wallet Address
```bash
python3 {baseDir}/scripts/wallet.py address
```

## Jupiter Swaps

### Get Swap Quote
```bash
python3 {baseDir}/scripts/jup_swap.py quote <input_token> <output_token> <amount>
python3 {baseDir}/scripts/jup_swap.py quote SOL USDC 1
```

### Execute Swap
```bash
python3 {baseDir}/scripts/jup_swap.py swap <input_token> <output_token> <amount>
python3 {baseDir}/scripts/jup_swap.py swap SOL USDC 0.1
```

### List Known Tokens
```bash
python3 {baseDir}/scripts/jup_swap.py tokens
```

Token symbols: SOL, USDC, USDT, BONK, JUP, RAY, PYTH (or use full mint addresses)

## Pump.fun Token Launch

### Launch Token
```bash
python3 {baseDir}/scripts/pumpfun.py launch --name "Token Name" --symbol "TKN" --image ./logo.png
```

### Launch with Dev Buy
```bash
python3 {baseDir}/scripts/pumpfun.py launch --name "Token Name" --symbol "TKN" --image ./logo.png --buy 0.5
```

### Launch with Custom Mint (Vanity Address)
```bash
python3 {baseDir}/scripts/pumpfun.py launch --name "Token Name" --symbol "TKN" --image ./logo.png --mint-key <base58_key>
```

Use vanity addresses ending in 'pump' for more legit-looking tokens. Generate with:
```bash
solana-keygen grind --ends-with pump:1
```

### Options
- `--name` - Token name (required)
- `--symbol` - Token symbol (required)
- `--image` - Path to token image (required)
- `--description` or `-d` - Token description
- `--buy` or `-b` - Dev buy amount in SOL
- `--mint-key` or `-m` - Custom mint private key (base58)

## Network Configuration

By default, wallet operations run on **mainnet**. Use `--network` to switch:

```bash
python3 {baseDir}/scripts/wallet.py balance --network devnet
python3 {baseDir}/scripts/wallet.py balance --network testnet
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SOLANA_PRIVATE_KEY` | Base58-encoded private key (required) |
| `JUPITER_API_KEY` | Jupiter API key for swaps (required) |
| `SOLANA_RPC_URL` | Custom RPC endpoint (optional) |

## Examples

```bash
# Initialize new wallet
python3 {baseDir}/scripts/initialize.py

# Check your SOL balance
python3 {baseDir}/scripts/wallet.py balance

# Send 0.1 SOL to another wallet
python3 {baseDir}/scripts/wallet.py send 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.1

# Check USDC balance (mainnet USDC mint)
python3 {baseDir}/scripts/wallet.py token-balance EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# Send 10 USDC to another wallet
python3 {baseDir}/scripts/wallet.py send-token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 10

# Quote swap: 1 SOL to USDC
python3 {baseDir}/scripts/jup_swap.py quote SOL USDC 1

# Swap 0.5 SOL to USDC
python3 {baseDir}/scripts/jup_swap.py swap SOL USDC 0.5

# Launch token on Pump.fun
python3 {baseDir}/scripts/pumpfun.py launch --name "My Token" --symbol "MTK" --image ./logo.png

# Launch with dev buy
python3 {baseDir}/scripts/pumpfun.py launch --name "My Token" --symbol "MTK" --image ./logo.png --buy 1
```

## Common Token Mints (Mainnet)

| Token | Mint Address |
|-------|--------------|
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |
| BONK | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` |

## When to Use

- **Create wallets** for new Solana accounts
- **Check balances** of SOL or any SPL token
- **Send SOL** for payments or transfers
- **Send tokens** for SPL token transfers
- **Swap tokens** via Jupiter aggregator
- **Launch tokens** on Pump.fun with custom images and dev buys
- **Devnet testing** with `--network devnet`
