# Kraken Crypto Skill

Use the kraken_cli.py wrapper to query your Kraken account.

## Setup

Export your Kraken API credentials.

```bash
export KRAKEN_API_KEY="your_api_key"
export KRAKEN_API_SECRET="your_api_secret"
```

You can also create a .env file in the skill directory.

## 1. Primary Commands

Use these commands for portfolio queries. They calculate totals automatically.

| Command | Description |
|---------|-------------|
| summary | Portfolio overview with correct totals |
| net-worth | Total net worth calculation |
| performance | Returns compared to deposits |
| holdings | Asset breakdown with USD values |
| staking | Staking positions and rewards |

### Example Output summary

```
TOTAL NET WORTH
  Main Wallet (Equity):    $544.95
  Earn Wallet (Bonded):    $81.89
  TOTAL:                   $626.84

AUTO EARN (Flexible) in Main Wallet
  BTC   : $493.92 (rewards: $0.03)
  ETH   : $50.66 (rewards: $0.11)

BONDED STAKING in Earn Wallet
  SOL   : $66.73 (rewards: $0.89)
  DOT   : $15.16 (rewards: $0.55)

  Total Staking Rewards:   $1.71
```

The wrapper separates Auto Earn from Bonded staking to avoid double counting.

## 2. Raw API Commands

These commands use kraken_api.py for detailed data. Use them for specific information not covered by primary commands.

### Market Data Public

| Command | Description | Use Case |
|---------|-------------|----------|
| ticker --pair XXBTZUSD | Current price and 24h stats | Price checks |
| ohlc --pair XXBTZUSD | Historical candles | Chart data |
| depth --pair XXBTZUSD | Order book | Liquidity analysis |
| recent-trades --pair XXBTZUSD | Live trades | Market activity |
| assets | Asset names and decimals | Asset lookups |
| pairs | Valid trading pairs | Pair discovery |
| status | Exchange status | Connectivity check |
| time | Server time | API health check |

### Account Data Private

| Command | Description | Use Case |
|---------|-------------|----------|
| balance | Raw asset quantities | Detailed holdings |
| balance-ex | Balance with reserved funds | Margin analysis |
| portfolio | Trade balance in USD | Raw equity data |
| open-orders | Active orders | Order management |
| closed-orders | Completed orders | Order history |
| trades | Trade execution history | Trade analysis |
| ledger | All transactions | Transaction tracking |
| ledger --asset ZUSD | Filtered by asset | Asset history |
| volume | 30 day volume | Fee tier info |

### Earn Data Private

| Command | Description | Use Case |
|---------|-------------|----------|
| earn-positions | Raw staking allocations | Detailed staking data |
| earn-strategies | Available yield programs | Strategy discovery |
| earn-status | Pending stakes | Allocation monitoring |
| earn-dealloc-status --refid ID | Pending unstakes | Deallocation monitoring |

### Funding Private

| Command | Description | Use Case |
|---------|-------------|----------|
| deposits-methods | Available deposit methods | Deposit options |
| deposits-address --asset BTC | Wallet address | Receiving crypto |

## 3. Critical Caveats

### Double Counting Warning

Do not add balance and earn-positions together.

Kraken has two staking types.
- Auto Earn Flexible assets stay in the Main wallet. These are included in portfolio equity.
- Bonded Staking assets move to the Earn wallet. These are not in portfolio equity.

The summary command handles this correctly. If you use raw commands manually follow this logic.
- Correct calculation is Total equals Portfolio Equity plus Bonded Earn Only.
- Incorrect calculation is Total equals Portfolio Equity plus All Earn Allocations.

### API Response Notes

- ohlc returns a list under the pair key.
- depth bids and asks are nested under the pair key.
- recent-trades returns a list containing price, volume, time, side, type, and misc.
- earn-strategies uses the items key with apr_estimate.

## 4. Example Usage

| User Request | Bot Action |
|--------------|------------|
| What is my crypto portfolio? | Run summary |
| What is my net worth? | Run net-worth |
| How am I performing? | Run performance |
| Show my holdings | Run holdings |
| Show my staking | Run staking |
| What is BTC price? | Run ticker --pair XXBTZUSD |
| Show my open orders | Run open-orders |
| Show my trade history | Run trades |
| Get my BTC deposit address | Run deposits-address --asset BTC |

## 5. API Key Permissions Required

| Feature | Permission |
|---------|------------|
| Balance and Portfolio | Query Funds |
| Orders and Trades and Ledgers | Query Funds |
| Earn Allocations | Earn |
| Deposit Addresses | Query Funds |
| Market Data | None |