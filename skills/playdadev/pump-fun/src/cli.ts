#!/usr/bin/env node

/**
 * CLI interface for Pump.fun Skill
 * Allows direct command-line usage for testing and scripting
 */

import { buyTokens, sellTokens } from './trade.js';
import { launchToken } from './launch.js';
import { getConfig } from './config.js';

const HELP_TEXT = `
Pump.fun Skill CLI

Usage:
  node cli.js <command> [options]

Commands:
  buy <mint> <amount_sol> [slippage]     Buy tokens with SOL
  sell <mint> <amount|percent> [slippage] Sell tokens (use "50%" for percentage)
  launch <name> <symbol> <description> [dev_buy_sol]  Launch a new token

Environment Variables:
  SOLANA_PRIVATE_KEY    Your Solana wallet private key (required)
  SOLANA_RPC_URL        Custom RPC endpoint (optional)
  PUMP_PRIORITY_FEE     Priority fee in SOL (default: 0.0005)
  PUMP_DEFAULT_SLIPPAGE Default slippage % (default: 10)

Examples:
  # Buy 0.1 SOL worth of tokens
  node cli.js buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.1

  # Buy with 15% slippage
  node cli.js buy 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 0.1 15

  # Sell 100% of tokens
  node cli.js sell 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 100%

  # Launch a new token
  node cli.js launch "My Token" MTK "The best token ever" 1
`;

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(HELP_TEXT);
    process.exit(0);
  }

  const command = args[0].toLowerCase();

  try {
    // Verify configuration is valid
    getConfig();

    switch (command) {
      case 'buy': {
        if (args.length < 3) {
          console.error('Usage: buy <mint> <amount_sol> [slippage]');
          process.exit(1);
        }

        const mint = args[1];
        const amountSol = parseFloat(args[2]);
        const slippage = args[3] ? parseInt(args[3]) : undefined;

        if (isNaN(amountSol) || amountSol <= 0) {
          console.error('Invalid amount. Must be a positive number.');
          process.exit(1);
        }

        console.log(`\nBuying ${amountSol} SOL worth of tokens...`);
        console.log(`Token: ${mint}`);
        if (slippage) console.log(`Slippage: ${slippage}%`);
        console.log('');

        const result = await buyTokens(mint, amountSol, { slippage });

        if (result.success && result.data) {
          console.log('\n✓ Purchase successful!');
          console.log(`  Transaction: ${result.data.signature}`);
          console.log(`  Explorer: ${result.data.explorerUrl}`);
        } else {
          console.error('\n✗ Purchase failed:', result.error);
          process.exit(1);
        }
        break;
      }

      case 'sell': {
        if (args.length < 3) {
          console.error('Usage: sell <mint> <amount|percent> [slippage]');
          process.exit(1);
        }

        const mint = args[1];
        const amount = args[2];
        const slippage = args[3] ? parseInt(args[3]) : undefined;

        console.log(`\nSelling ${amount} tokens...`);
        console.log(`Token: ${mint}`);
        if (slippage) console.log(`Slippage: ${slippage}%`);
        console.log('');

        const result = await sellTokens(mint, amount, { slippage });

        if (result.success && result.data) {
          console.log('\n✓ Sale successful!');
          console.log(`  Transaction: ${result.data.signature}`);
          console.log(`  Explorer: ${result.data.explorerUrl}`);
        } else {
          console.error('\n✗ Sale failed:', result.error);
          process.exit(1);
        }
        break;
      }

      case 'launch': {
        if (args.length < 4) {
          console.error('Usage: launch <name> <symbol> <description> [dev_buy_sol]');
          process.exit(1);
        }

        const name = args[1];
        const symbol = args[2];
        const description = args[3];
        const devBuyAmountSol = args[4] ? parseFloat(args[4]) : 0;

        console.log(`\nLaunching new token...`);
        console.log(`  Name: ${name}`);
        console.log(`  Symbol: ${symbol}`);
        console.log(`  Description: ${description}`);
        console.log(`  Dev buy: ${devBuyAmountSol} SOL`);
        console.log('');

        const result = await launchToken(name, symbol, description, { devBuyAmountSol });

        if (result.success && result.data) {
          console.log('\n✓ Token launched successfully!');
          console.log(`  Mint Address: ${result.data.mintAddress}`);
          console.log(`  Transaction: ${result.data.signature}`);
          console.log(`  Explorer: ${result.data.explorerUrl}`);
          console.log(`  Pump.fun: ${result.data.pumpFunUrl}`);
        } else {
          console.error('\n✗ Launch failed:', result.error);
          process.exit(1);
        }
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        console.log(HELP_TEXT);
        process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
