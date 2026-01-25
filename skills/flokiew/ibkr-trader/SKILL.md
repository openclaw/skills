---
name: ibkr-trading
description: Interactive Brokers (IBKR) trading automation via Client Portal API. Use when setting up IBKR account access, authenticating sessions, checking portfolio/positions, or building trading bots. Handles IBeam automated login with IBKR Key 2FA.
---

# IBKR Trading Skill

Automate trading with Interactive Brokers using the Client Portal Gateway API.

## Overview

This skill enables:
- Automated IBKR authentication via IBeam + IBKR Key
- Portfolio and position monitoring
- Order placement and management
- Building custom trading strategies

## Prerequisites

- IBKR account (live or paper)
- IBKR Key app installed on phone (for 2FA)
- Linux server with Java 11+ and Chrome/Chromium

## Quick Setup

### 1. Install Dependencies

```bash
# Java (for Client Portal Gateway)
sudo apt-get install -y openjdk-17-jre-headless

# Chrome + ChromeDriver (for IBeam)
sudo apt-get install -y chromium-browser chromium-chromedriver

# Virtual display (headless auth)
sudo apt-get install -y xvfb

# Python venv
python3 -m venv ~/trading/venv
source ~/trading/venv/bin/activate
pip install ibeam requests
```

### 2. Download Client Portal Gateway

```bash
cd ~/trading
wget https://download2.interactivebrokers.com/portal/clientportal.gw.zip
unzip clientportal.gw.zip -d clientportal
```

### 3. Configure Credentials

Create `~/trading/.env`:
```bash
IBEAM_ACCOUNT=your_username
IBEAM_PASSWORD='your_password'
IBEAM_GATEWAY_DIR=/path/to/trading/clientportal
IBEAM_CHROME_DRIVER_PATH=/usr/bin/chromedriver
IBEAM_TWO_FA_SELECT_TARGET="IB Key"
```

## Authentication

### Start Gateway + Authenticate

```bash
# 1. Start Client Portal Gateway
cd ~/trading/clientportal && bash bin/run.sh root/conf.yaml &

# 2. Wait for startup (~20 sec)
sleep 20

# 3. Run IBeam authentication
cd ~/trading
source venv/bin/activate
source .env
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
python -m ibeam --authenticate
```

**Important:** User must approve IBKR Key notification on phone within ~2 minutes!

### Check Auth Status

```bash
curl -sk https://localhost:5000/v1/api/iserver/auth/status
```

Authenticated response includes `"authenticated": true`.

## API Usage

### Account Info

```bash
# List accounts
curl -sk https://localhost:5000/v1/api/portfolio/accounts

# Account summary
curl -sk "https://localhost:5000/v1/api/portfolio/{accountId}/summary"
```

### Positions

```bash
# Current positions
curl -sk "https://localhost:5000/v1/api/portfolio/{accountId}/positions/0"
```

### Market Data

```bash
# Search for symbol
curl -sk "https://localhost:5000/v1/api/iserver/secdef/search?symbol=AAPL"

# Get quote (after searching)
curl -sk "https://localhost:5000/v1/api/iserver/marketdata/snapshot?conids=265598&fields=31,84,86"
```

### Place Orders

```bash
curl -sk -X POST "https://localhost:5000/v1/api/iserver/account/{accountId}/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [{
      "conid": 265598,
      "orderType": "MKT",
      "side": "BUY",
      "quantity": 1,
      "tif": "DAY"
    }]
  }'
```

## Session Management

Sessions expire after ~24 hours. Options:

1. **Keepalive cron** - Ping `/v1/api/tickle` every 5 min
2. **Auto re-auth** - Run IBeam when session expires (requires phone approval)

### Keepalive Script

```python
import requests
import urllib3
urllib3.disable_warnings()

def keepalive():
    try:
        r = requests.post("https://localhost:5000/v1/api/tickle", verify=False, timeout=10)
        status = requests.get("https://localhost:5000/v1/api/iserver/auth/status", verify=False, timeout=10)
        return status.json().get("authenticated", False)
    except:
        return False
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gateway not responding | Check if Java process is running: `ps aux \| grep GatewayStart` |
| Login timeout | User didn't approve IBKR Key in time - retry auth |
| Connection refused | Gateway not started - run `bin/run.sh root/conf.yaml` |
| Chrome errors | Ensure Xvfb is running: `Xvfb :99 &` and `export DISPLAY=:99` |

## Files Reference

See `references/api-endpoints.md` for complete API documentation.
See `scripts/` for ready-to-use automation scripts.
