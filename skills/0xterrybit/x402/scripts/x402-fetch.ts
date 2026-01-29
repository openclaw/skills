#!/usr/bin/env npx ts-node
/**
 * x402-fetch.ts - Simple x402 payment-enabled fetch wrapper
 * 
 * Usage:
 *   npx ts-node x402-fetch.ts <url> [options]
 *   
 * Options:
 *   --method POST|GET|...
 *   --body '{"key":"value"}'
 *   --network base|ethereum|arbitrum
 *   --dry-run  (show payment details without paying)
 * 
 * Environment:
 *   WALLET_PRIVATE_KEY - Required for signing payments
 */

import { createWalletClient, http, parseUnits, encodeFunctionData } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base, mainnet, arbitrum, optimism, polygon } from 'viem/chains';

const NETWORKS: Record<string, any> = {
  base: { chain: base, rpc: process.env.BASE_RPC_URL || 'https://mainnet.base.org' },
  ethereum: { chain: mainnet, rpc: process.env.ETH_RPC_URL || 'https://eth.llamarpc.com' },
  arbitrum: { chain: arbitrum, rpc: process.env.ARB_RPC_URL || 'https://arb1.arbitrum.io/rpc' },
  optimism: { chain: optimism, rpc: process.env.OP_RPC_URL || 'https://mainnet.optimism.io' },
  polygon: { chain: polygon, rpc: process.env.POLYGON_RPC_URL || 'https://polygon-rpc.com' },
};

// USDC addresses per network
const USDC_ADDRESSES: Record<string, `0x${string}`> = {
  base: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  ethereum: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  arbitrum: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
  optimism: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
  polygon: '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
};

interface PaymentRequirement {
  amount: string;
  currency: string;
  network: string;
  recipient: string;
  scheme: string;
  facilitator?: string;
}

async function parseArgs() {
  const args = process.argv.slice(2);
  const url = args[0];
  
  if (!url || url.startsWith('--')) {
    console.error('Usage: x402-fetch.ts <url> [--method POST] [--body "{}"] [--network base] [--dry-run]');
    process.exit(1);
  }

  const options: any = { url, method: 'GET', network: 'base', dryRun: false };
  
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--method') options.method = args[++i];
    else if (args[i] === '--body') options.body = args[++i];
    else if (args[i] === '--network') options.network = args[++i];
    else if (args[i] === '--dry-run') options.dryRun = true;
  }

  return options;
}

function decodePaymentRequired(header: string): PaymentRequirement[] {
  try {
    const decoded = JSON.parse(Buffer.from(header, 'base64').toString('utf-8'));
    return Array.isArray(decoded) ? decoded : [decoded];
  } catch {
    throw new Error('Failed to decode PAYMENT-REQUIRED header');
  }
}

async function createPaymentSignature(
  requirement: PaymentRequirement,
  privateKey: string
): Promise<string> {
  const networkConfig = NETWORKS[requirement.network];
  if (!networkConfig) throw new Error(`Unsupported network: ${requirement.network}`);

  const account = privateKeyToAccount(privateKey as `0x${string}`);
  const client = createWalletClient({
    account,
    chain: networkConfig.chain,
    transport: http(networkConfig.rpc),
  });

  // Create EIP-712 typed data for x402 payment
  const domain = {
    name: 'x402',
    version: '2',
    chainId: networkConfig.chain.id,
  };

  const types = {
    Payment: [
      { name: 'recipient', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'token', type: 'address' },
      { name: 'nonce', type: 'uint256' },
    ],
  };

  const usdcAddress = USDC_ADDRESSES[requirement.network];
  const nonce = Date.now();

  const message = {
    recipient: requirement.recipient as `0x${string}`,
    amount: BigInt(requirement.amount),
    token: usdcAddress,
    nonce: BigInt(nonce),
  };

  const signature = await client.signTypedData({
    domain,
    types,
    primaryType: 'Payment',
    message,
  });

  // Create payment payload
  const payload = {
    signature,
    sender: account.address,
    nonce,
    network: requirement.network,
    scheme: requirement.scheme,
  };

  return Buffer.from(JSON.stringify(payload)).toString('base64');
}

async function x402Fetch(options: any) {
  const { url, method, body, network, dryRun } = options;
  
  console.log(`[x402] Requesting: ${method} ${url}`);

  // Step 1: Initial request
  const initialResponse = await fetch(url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body,
  });

  // If not 402, return response directly
  if (initialResponse.status !== 402) {
    console.log(`[x402] Response: ${initialResponse.status} (no payment required)`);
    return initialResponse;
  }

  // Step 2: Parse payment requirements
  const paymentHeader = initialResponse.headers.get('PAYMENT-REQUIRED');
  if (!paymentHeader) {
    throw new Error('402 response missing PAYMENT-REQUIRED header');
  }

  const requirements = decodePaymentRequired(paymentHeader);
  console.log('[x402] Payment required:');
  requirements.forEach((req, i) => {
    const amount = Number(req.amount) / 1e6; // Assuming USDC 6 decimals
    console.log(`  [${i}] ${amount} ${req.currency} on ${req.network} → ${req.recipient.slice(0, 10)}...`);
  });

  if (dryRun) {
    console.log('[x402] Dry run - not paying');
    return initialResponse;
  }

  // Step 3: Select requirement matching preferred network
  const requirement = requirements.find(r => r.network === network) || requirements[0];
  console.log(`[x402] Selected: ${requirement.network}`);

  // Step 4: Create payment signature
  const privateKey = process.env.WALLET_PRIVATE_KEY;
  if (!privateKey) {
    throw new Error('WALLET_PRIVATE_KEY environment variable required');
  }

  console.log('[x402] Signing payment...');
  const paymentSignature = await createPaymentSignature(requirement, privateKey);

  // Step 5: Retry with payment
  console.log('[x402] Retrying with payment...');
  const paidResponse = await fetch(url, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      'PAYMENT-SIGNATURE': paymentSignature,
    },
    body,
  });

  console.log(`[x402] Response: ${paidResponse.status}`);
  
  if (paidResponse.status === 200) {
    const paymentResponse = paidResponse.headers.get('PAYMENT-RESPONSE');
    if (paymentResponse) {
      const settlement = JSON.parse(Buffer.from(paymentResponse, 'base64').toString());
      console.log(`[x402] Payment settled: ${settlement.txHash || 'confirmed'}`);
    }
  }

  return paidResponse;
}

// Main
(async () => {
  try {
    const options = await parseArgs();
    const response = await x402Fetch(options);
    
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await response.json();
      console.log('\n--- Response ---');
      console.log(JSON.stringify(data, null, 2));
    } else {
      const text = await response.text();
      console.log('\n--- Response ---');
      console.log(text);
    }
  } catch (err: any) {
    console.error(`[x402] Error: ${err.message}`);
    process.exit(1);
  }
})();
