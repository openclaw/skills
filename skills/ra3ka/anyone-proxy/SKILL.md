---
name: anyone-proxy
homepage: https://anyone.io
description: This skill enables IP address masking and accessing hidden services on the Anyone Network. Route requests through the Anyone Protocol VPN network using a local SOCKS5 proxy.
metadata:
  clawdbot:
    requires:
      packages:
        - "@anyone-protocol/anyone-client"
---

# Anyone Protocol Proxy Skill

This skill enables Clawdbot to route requests through the Anyone Protocol network.

## How It Works

The skill uses the `@anyone-protocol/anyone-client` NPM package to:
1. Start a local SOCKS5 proxy server (default port: 9050)
2. Create encrypted circuits through the Anyone Network
3. Route traffic through these circuits
4. Return responses while keeping the origin IP hidden

## Setup

### Install anyone-client
```bash
npm install -g @anyone-protocol/anyone-client
```

### Start the proxy
```bash
npx @anyone-protocol/anyone-client -s 9050
```

## Usage

Once the proxy is running, route requests through it:
```bash
# Using curl to verify IP
curl --socks5-hostname localhost:9050 https://check.en.anyone.tech/api/ip
```
```javascript
import { Anon } from "@anyone-protocol/anyone-client";
import { AnonSocksClient } from "@anyone-protocol/anyone-client";

async function main() {
    const anon = new Anon();
    const anonSocksClient = new AnonSocksClient(anon);

    try {
        await anon.start();
        // Wait for circuits to establish
        await new Promise(resolve => setTimeout(resolve, 15000));
        
        const response = await anonSocksClient.get('https://check.en.anyone.tech/api/ip');
        console.log('Response:', response.data);
        
    } catch(error) {
        console.error('Error:', error);
    } finally {
        await anon.stop();
    }
}

main();
```

## Notes

- First connection may take up to 30 seconds while circuits are established
- The proxy persists across requests once started