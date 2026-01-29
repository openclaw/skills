/**
 * Configuration module for Pump.fun skill
 * Handles environment variables and default settings
 */

export interface PumpConfig {
  privateKey: string;
  rpcUrl: string;
  priorityFee: number;
  defaultSlippage: number;
}

const DEFAULT_RPC_URL = 'https://api.mainnet-beta.solana.com';
const DEFAULT_PRIORITY_FEE = 0.0005;
const DEFAULT_SLIPPAGE = 10;

export function getConfig(): PumpConfig {
  const privateKey = process.env.SOLANA_PRIVATE_KEY;

  if (!privateKey) {
    throw new Error(
      'SOLANA_PRIVATE_KEY environment variable is required.\n' +
      'Set it with: export SOLANA_PRIVATE_KEY="your-base58-private-key"'
    );
  }

  return {
    privateKey,
    rpcUrl: process.env.SOLANA_RPC_URL || DEFAULT_RPC_URL,
    priorityFee: parseFloat(process.env.PUMP_PRIORITY_FEE || '') || DEFAULT_PRIORITY_FEE,
    defaultSlippage: parseInt(process.env.PUMP_DEFAULT_SLIPPAGE || '') || DEFAULT_SLIPPAGE,
  };
}

export const PUMPPORTAL_API = {
  TRADE_LOCAL: 'https://pumpportal.fun/api/trade-local',
  IPFS_UPLOAD: 'https://pump.fun/api/ipfs',
} as const;

export const SUPPORTED_POOLS = [
  'pump',
  'raydium',
  'pump-amm',
  'launchlab',
  'raydium-cpmm',
  'bonk',
  'auto',
] as const;

export type SupportedPool = typeof SUPPORTED_POOLS[number];
