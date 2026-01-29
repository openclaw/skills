/**
 * Pump.fun Skill for MoltBot
 *
 * Provides trading and token launching capabilities on Pump.fun
 * using the PumpPortal Local Transaction API.
 *
 * @module pump-fun-skill
 */

// Re-export all public APIs
export { buyTokens, sellTokens, simulateTrade } from './trade.js';
export type { TradeParams, TradeResult } from './trade.js';

export { launchToken, validateMetadata } from './launch.js';
export type { TokenMetadata, LaunchParams, LaunchResult } from './launch.js';

export { getConfig, PUMPPORTAL_API, SUPPORTED_POOLS } from './config.js';
export type { PumpConfig, SupportedPool } from './config.js';

export {
  getKeypairFromPrivateKey,
  getConnection,
  isValidSolanaAddress,
  parseAmount,
  formatTransactionUrl,
  formatSol,
} from './utils.js';
export type { OperationResult } from './utils.js';

// Version info
export const VERSION = '1.0.0';

/**
 * Quick start example:
 *
 * ```typescript
 * import { buyTokens, sellTokens, launchToken } from 'pump-fun-skill';
 *
 * // Buy 0.1 SOL worth of tokens
 * const buyResult = await buyTokens('TOKEN_MINT_ADDRESS', 0.1);
 *
 * // Sell 50% of your tokens
 * const sellResult = await sellTokens('TOKEN_MINT_ADDRESS', '50%');
 *
 * // Launch a new token with 1 SOL dev buy
 * const launchResult = await launchToken(
 *   'My Token',
 *   'MTK',
 *   'An awesome token',
 *   { devBuyAmountSol: 1 }
 * );
 * ```
 */
