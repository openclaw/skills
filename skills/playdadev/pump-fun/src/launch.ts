/**
 * Token Launch module for Pump.fun
 * Handles creating and launching new tokens
 */

import { TransactionSignature } from '@solana/web3.js';
import { getConfig, PUMPPORTAL_API } from './config.js';
import {
  getKeypairFromPrivateKey,
  getConnection,
  formatTransactionUrl,
  generateMintKeypair,
  safeExecute,
  OperationResult,
} from './utils.js';

export interface TokenMetadata {
  name: string;
  symbol: string;
  description: string;
  twitter?: string;
  telegram?: string;
  website?: string;
  showName?: boolean;
}

export interface LaunchParams {
  metadata: TokenMetadata;
  imagePath?: string;
  imageUrl?: string;
  devBuyAmountSol?: number;
  slippage?: number;
  priorityFee?: number;
}

export interface LaunchResult {
  signature: TransactionSignature;
  explorerUrl: string;
  mintAddress: string;
  tokenName: string;
  tokenSymbol: string;
  pumpFunUrl: string;
}

interface IpfsUploadResult {
  metadataUri: string;
}

interface CreateTokenRequest {
  publicKey: string;
  action: 'create';
  tokenMetadata: {
    name: string;
    symbol: string;
    uri: string;
  };
  mint: string;
  denominatedInSol: string;
  amount: number;
  slippage: number;
  priorityFee: number;
  pool: string;
}

/**
 * Uploads token metadata and image to IPFS via Pump.fun's API.
 * Uses Node's built-in FormData/Blob (not the form-data npm package)
 * to ensure compatibility with pump.fun's server.
 */
async function uploadToIpfs(
  metadata: TokenMetadata,
  imageSource?: { path?: string; url?: string }
): Promise<string> {
  const fs = await import('fs');

  let imageBuffer: Buffer;
  let fileName = 'image.png';

  if (imageSource?.path) {
    if (!fs.existsSync(imageSource.path)) {
      throw new Error(`Image file not found: ${imageSource.path}`);
    }
    imageBuffer = fs.readFileSync(imageSource.path) as Buffer;
    fileName = imageSource.path.split('/').pop() || 'image.png';
  } else if (imageSource?.url) {
    const imageResponse = await fetch(imageSource.url);
    if (!imageResponse.ok) {
      throw new Error(`Failed to fetch image from URL: ${imageSource.url}`);
    }
    imageBuffer = Buffer.from(await imageResponse.arrayBuffer());
  } else {
    console.warn('No image provided. Using placeholder. Consider providing an image for better token visibility.');
    imageBuffer = Buffer.from([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
      0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
      0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
      0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
    ]);
    fileName = 'placeholder.png';
  }

  // Use Node's built-in FormData + Blob (compatible with pump.fun)
  const blob = new Blob([imageBuffer], { type: 'image/png' });
  const formData = new FormData();
  formData.append('name', metadata.name);
  formData.append('symbol', metadata.symbol);
  formData.append('description', metadata.description);
  formData.append('showName', metadata.showName ? 'true' : 'false');
  if (metadata.twitter) formData.append('twitter', metadata.twitter);
  if (metadata.telegram) formData.append('telegram', metadata.telegram);
  if (metadata.website) formData.append('website', metadata.website);
  formData.append('file', blob, fileName);

  const response = await fetch(PUMPPORTAL_API.IPFS_UPLOAD, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`IPFS upload failed (${response.status}): ${errorText}`);
  }

  const result = (await response.json()) as IpfsUploadResult;

  if (!result.metadataUri) {
    throw new Error('IPFS upload did not return a metadata URI');
  }

  return result.metadataUri;
}

/**
 * Creates and launches a new token on Pump.fun
 */
async function executeTokenLaunch(params: LaunchParams): Promise<LaunchResult> {
  const config = getConfig();

  // Get keypair from private key
  const creatorKeypair = getKeypairFromPrivateKey(config.privateKey);
  const connection = getConnection();

  // Generate a new keypair for the token mint
  const mintKeypair = generateMintKeypair();
  const mintPublicKey = mintKeypair.publicKey.toBase58();

  console.log('Uploading token metadata to IPFS...');

  // Upload metadata to IPFS
  const metadataUri = await uploadToIpfs(params.metadata, {
    path: params.imagePath,
    url: params.imageUrl,
  });

  console.log(`Metadata uploaded: ${metadataUri}`);
  console.log('Preparing token creation transaction...');

  // Prepare the create request
  const createRequest: CreateTokenRequest = {
    publicKey: creatorKeypair.publicKey.toBase58(),
    action: 'create',
    tokenMetadata: {
      name: params.metadata.name,
      symbol: params.metadata.symbol,
      uri: metadataUri,
    },
    mint: mintKeypair.publicKey.toBase58(),
    denominatedInSol: 'true',
    amount: params.devBuyAmountSol ?? 0,
    slippage: params.slippage ?? config.defaultSlippage,
    priorityFee: params.priorityFee ?? config.priorityFee,
    pool: 'pump',
  };

  console.log(`Creating token: ${params.metadata.name} (${params.metadata.symbol})`);
  console.log(`  Mint address: ${mintPublicKey}`);
  console.log(`  Dev buy: ${createRequest.amount} SOL`);

  // Fetch serialized transaction from PumpPortal
  const response = await fetch(PUMPPORTAL_API.TRADE_LOCAL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(createRequest),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Token creation failed (${response.status}): ${errorText}`);
  }

  const serializedTx = new Uint8Array(await response.arrayBuffer());

  console.log('Transaction received, signing and sending...');

  // Sign with both creator and mint keypairs
  const { VersionedTransaction } = await import('@solana/web3.js');
  const transaction = VersionedTransaction.deserialize(serializedTx);
  transaction.sign([creatorKeypair, mintKeypair]);

  // Send the transaction
  const signature = await connection.sendTransaction(transaction, {
    skipPreflight: false,
    preflightCommitment: 'confirmed',
    maxRetries: 3,
  });

  // Wait for confirmation
  const latestBlockhash = await connection.getLatestBlockhash();
  await connection.confirmTransaction({
    signature,
    blockhash: latestBlockhash.blockhash,
    lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
  });

  console.log('Token launched successfully!');
  console.log(`  Signature: ${signature}`);
  console.log(`  Mint: ${mintPublicKey}`);

  return {
    signature,
    explorerUrl: formatTransactionUrl(signature),
    mintAddress: mintPublicKey,
    tokenName: params.metadata.name,
    tokenSymbol: params.metadata.symbol,
    pumpFunUrl: `https://pump.fun/${mintPublicKey}`,
  };
}

/**
 * Launch a new token on Pump.fun
 *
 * @param name - Token name
 * @param symbol - Token symbol/ticker
 * @param description - Token description
 * @param options - Optional parameters (image, socials, dev buy amount)
 */
export async function launchToken(
  name: string,
  symbol: string,
  description: string,
  options: Partial<Omit<LaunchParams, 'metadata'>> & {
    twitter?: string;
    telegram?: string;
    website?: string;
  } = {}
): Promise<OperationResult<LaunchResult>> {
  const metadata: TokenMetadata = {
    name,
    symbol,
    description,
    twitter: options.twitter,
    telegram: options.telegram,
    website: options.website,
    showName: true,
  };

  return safeExecute(
    () => executeTokenLaunch({
      metadata,
      imagePath: options.imagePath,
      imageUrl: options.imageUrl,
      devBuyAmountSol: options.devBuyAmountSol,
      slippage: options.slippage,
      priorityFee: options.priorityFee,
    }),
    'Launch token'
  );
}

/**
 * Validate token metadata before launch
 */
export function validateMetadata(metadata: TokenMetadata): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!metadata.name || metadata.name.length === 0) {
    errors.push('Token name is required');
  } else if (metadata.name.length > 32) {
    errors.push('Token name must be 32 characters or less');
  }

  if (!metadata.symbol || metadata.symbol.length === 0) {
    errors.push('Token symbol is required');
  } else if (metadata.symbol.length > 10) {
    errors.push('Token symbol must be 10 characters or less');
  }

  if (!metadata.description || metadata.description.length === 0) {
    errors.push('Token description is required');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
