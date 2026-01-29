/**
 * Utility functions for Pump.fun skill
 */

import {
  Connection,
  Keypair,
  VersionedTransaction,
  TransactionSignature,
  SendOptions,
} from '@solana/web3.js';
import bs58 from 'bs58';
import { getConfig } from './config.js';

/**
 * Creates a Keypair from a base58 encoded private key
 */
export function getKeypairFromPrivateKey(privateKeyBase58: string): Keypair {
  try {
    const privateKeyBytes = bs58.decode(privateKeyBase58);
    return Keypair.fromSecretKey(privateKeyBytes);
  } catch (error) {
    throw new Error(
      'Invalid private key format. Ensure SOLANA_PRIVATE_KEY is a valid base58 encoded key.'
    );
  }
}

/**
 * Creates a Solana connection using configured RPC URL
 */
export function getConnection(): Connection {
  const config = getConfig();
  return new Connection(config.rpcUrl, 'confirmed');
}

/**
 * Signs and sends a serialized transaction
 */
export async function signAndSendTransaction(
  serializedTransaction: Uint8Array,
  keypair: Keypair,
  connection: Connection
): Promise<TransactionSignature> {
  // Deserialize the transaction
  const transaction = VersionedTransaction.deserialize(serializedTransaction);

  // Sign the transaction
  transaction.sign([keypair]);

  // Send the transaction
  const sendOptions: SendOptions = {
    skipPreflight: false,
    preflightCommitment: 'confirmed',
    maxRetries: 3,
  };

  const signature = await connection.sendTransaction(transaction, sendOptions);

  // Wait for confirmation
  const latestBlockhash = await connection.getLatestBlockhash();
  await connection.confirmTransaction({
    signature,
    blockhash: latestBlockhash.blockhash,
    lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
  });

  return signature;
}

/**
 * Validates a Solana address (mint or wallet)
 */
export function isValidSolanaAddress(address: string): boolean {
  try {
    const decoded = bs58.decode(address);
    return decoded.length === 32;
  } catch {
    return false;
  }
}

/**
 * Parses amount string, handling percentage notation
 */
export function parseAmount(amountStr: string): { value: number; isPercentage: boolean } {
  const isPercentage = amountStr.endsWith('%');
  const cleanedStr = isPercentage ? amountStr.slice(0, -1) : amountStr;
  const value = parseFloat(cleanedStr);

  if (isNaN(value) || value <= 0) {
    throw new Error(`Invalid amount: ${amountStr}`);
  }

  if (isPercentage && (value < 0 || value > 100)) {
    throw new Error(`Percentage must be between 0 and 100, got: ${value}`);
  }

  return { value, isPercentage };
}

/**
 * Formats a transaction signature for display
 */
export function formatTransactionUrl(signature: string): string {
  return `https://solscan.io/tx/${signature}`;
}

/**
 * Formats SOL amount with proper decimals
 */
export function formatSol(lamports: number): string {
  return (lamports / 1e9).toFixed(6);
}

/**
 * Sleep utility for rate limiting
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Generates a new keypair for token mint
 */
export function generateMintKeypair(): Keypair {
  return Keypair.generate();
}

/**
 * Result type for operations
 */
export interface OperationResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Wraps an async operation with error handling
 */
export async function safeExecute<T>(
  operation: () => Promise<T>,
  operationName: string
): Promise<OperationResult<T>> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`${operationName} failed:`, errorMessage);
    return { success: false, error: errorMessage };
  }
}
