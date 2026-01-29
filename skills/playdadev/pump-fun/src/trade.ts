/**
 * Trading module for Pump.fun
 * Handles buying and selling tokens using the PumpPortal Local Transaction API
 */

import { Keypair, TransactionSignature } from '@solana/web3.js';
import { getConfig, PUMPPORTAL_API, SupportedPool } from './config.js';
import {
  getKeypairFromPrivateKey,
  getConnection,
  signAndSendTransaction,
  isValidSolanaAddress,
  parseAmount,
  formatTransactionUrl,
  safeExecute,
  OperationResult,
} from './utils.js';

export interface TradeParams {
  mint: string;
  amount: number | string;
  slippage?: number;
  priorityFee?: number;
  pool?: SupportedPool;
  denominatedInSol?: boolean;
}

export interface TradeResult {
  signature: TransactionSignature;
  explorerUrl: string;
  action: 'buy' | 'sell';
  mint: string;
  amount: string;
}

interface PumpPortalTradeRequest {
  publicKey: string;
  action: 'buy' | 'sell';
  mint: string;
  amount: number | string;
  denominatedInSol: string;
  slippage: number;
  priorityFee: number;
  pool: string;
}

/**
 * Fetches a serialized transaction from PumpPortal Local API
 */
async function fetchLocalTransaction(params: PumpPortalTradeRequest): Promise<Uint8Array> {
  const response = await fetch(PUMPPORTAL_API.TRADE_LOCAL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`PumpPortal API error (${response.status}): ${errorText}`);
  }

  const arrayBuffer = await response.arrayBuffer();
  return new Uint8Array(arrayBuffer);
}

/**
 * Executes a trade (buy or sell) on Pump.fun
 */
async function executeTrade(
  action: 'buy' | 'sell',
  params: TradeParams
): Promise<TradeResult> {
  const config = getConfig();

  // Validate mint address
  if (!isValidSolanaAddress(params.mint)) {
    throw new Error(`Invalid token mint address: ${params.mint}`);
  }

  // Get keypair from private key
  const keypair = getKeypairFromPrivateKey(config.privateKey);
  const connection = getConnection();

  // Parse amount (handle percentage for sells)
  let amount: number | string;
  let denominatedInSol: boolean;

  if (typeof params.amount === 'string' && params.amount.includes('%')) {
    // Percentage sell
    if (action !== 'sell') {
      throw new Error('Percentage amounts are only supported for selling');
    }
    amount = params.amount; // Pass percentage string directly
    denominatedInSol = false;
  } else {
    amount = typeof params.amount === 'string' ? parseFloat(params.amount) : params.amount;
    denominatedInSol = params.denominatedInSol ?? (action === 'buy');
  }

  // Prepare request parameters
  const requestParams: PumpPortalTradeRequest = {
    publicKey: keypair.publicKey.toBase58(),
    action,
    mint: params.mint,
    amount,
    denominatedInSol: denominatedInSol ? 'true' : 'false',
    slippage: params.slippage ?? config.defaultSlippage,
    priorityFee: params.priorityFee ?? config.priorityFee,
    pool: params.pool ?? 'auto',
  };

  console.log(`Preparing ${action} transaction...`);
  console.log(`  Mint: ${params.mint}`);
  console.log(`  Amount: ${amount}${denominatedInSol ? ' SOL' : ' tokens'}`);
  console.log(`  Slippage: ${requestParams.slippage}%`);
  console.log(`  Pool: ${requestParams.pool}`);

  // Fetch serialized transaction from PumpPortal
  const serializedTx = await fetchLocalTransaction(requestParams);

  console.log('Transaction received, signing and sending...');

  // Sign and send the transaction
  const signature = await signAndSendTransaction(serializedTx, keypair, connection);

  console.log(`Transaction confirmed!`);
  console.log(`  Signature: ${signature}`);

  return {
    signature,
    explorerUrl: formatTransactionUrl(signature),
    action,
    mint: params.mint,
    amount: String(amount),
  };
}

/**
 * Buy tokens on Pump.fun
 *
 * @param mint - Token mint address (contract address)
 * @param amountSol - Amount of SOL to spend
 * @param options - Optional parameters (slippage, priorityFee, pool)
 */
export async function buyTokens(
  mint: string,
  amountSol: number,
  options: Partial<Omit<TradeParams, 'mint' | 'amount'>> = {}
): Promise<OperationResult<TradeResult>> {
  return safeExecute(
    () => executeTrade('buy', {
      mint,
      amount: amountSol,
      denominatedInSol: true,
      ...options,
    }),
    'Buy tokens'
  );
}

/**
 * Sell tokens on Pump.fun
 *
 * @param mint - Token mint address (contract address)
 * @param amount - Amount of tokens to sell (number) or percentage string (e.g., "50%", "100%")
 * @param options - Optional parameters (slippage, priorityFee, pool)
 */
export async function sellTokens(
  mint: string,
  amount: number | string,
  options: Partial<Omit<TradeParams, 'mint' | 'amount'>> = {}
): Promise<OperationResult<TradeResult>> {
  return safeExecute(
    () => executeTrade('sell', {
      mint,
      amount,
      denominatedInSol: false,
      ...options,
    }),
    'Sell tokens'
  );
}

/**
 * Get estimated output for a trade (simulation)
 * Note: This performs a preflight check without actually executing
 */
export async function simulateTrade(
  action: 'buy' | 'sell',
  params: TradeParams
): Promise<OperationResult<{ valid: boolean; message: string }>> {
  return safeExecute(async () => {
    const config = getConfig();
    const keypair = getKeypairFromPrivateKey(config.privateKey);

    // Parse amount
    let amount: number | string;
    let denominatedInSol: boolean;

    if (typeof params.amount === 'string' && params.amount.includes('%')) {
      amount = params.amount;
      denominatedInSol = false;
    } else {
      amount = typeof params.amount === 'string' ? parseFloat(params.amount) : params.amount;
      denominatedInSol = params.denominatedInSol ?? (action === 'buy');
    }

    const requestParams: PumpPortalTradeRequest = {
      publicKey: keypair.publicKey.toBase58(),
      action,
      mint: params.mint,
      amount,
      denominatedInSol: denominatedInSol ? 'true' : 'false',
      slippage: params.slippage ?? config.defaultSlippage,
      priorityFee: params.priorityFee ?? config.priorityFee,
      pool: params.pool ?? 'auto',
    };

    // Try to fetch transaction - if successful, the trade is valid
    await fetchLocalTransaction(requestParams);

    return {
      valid: true,
      message: `Trade simulation successful. Ready to ${action} ${amount} ${denominatedInSol ? 'SOL worth of' : ''} tokens.`,
    };
  }, 'Simulate trade');
}
