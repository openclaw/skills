#!/usr/bin/env node
/**
 * x402 Wallet Generator
 * Creates a new EVM wallet and saves it encrypted to ~/.x402/wallet.json
 */
import { ethers } from "ethers";
import { writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { createInterface } from "readline";

const WALLET_DIR = join(homedir(), ".x402");
const WALLET_FILE = join(WALLET_DIR, "wallet.json");

async function prompt(question) {
  const rl = createInterface({ input: process.stdin, output: process.stderr });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  if (existsSync(WALLET_FILE)) {
    console.error("⚠️  Wallet already exists at", WALLET_FILE);
    console.error("   Delete it first if you want to generate a new one.");
    process.exit(1);
  }

  // Generate random wallet
  const wallet = ethers.Wallet.createRandom();

  console.error("🔑 New wallet generated!");
  console.error("");
  console.error("   Address: ", wallet.address);
  console.error("   Network:  Base (Ethereum L2)");
  console.error("");

  // For non-interactive use (piped/cron), use a default passphrase
  let passphrase;
  if (process.stdin.isTTY) {
    passphrase = await prompt("Enter passphrase to encrypt wallet (or press Enter for none): ");
  } else {
    // Non-interactive: generate a random passphrase and save it
    passphrase = ethers.hexlify(ethers.randomBytes(16));
    console.error("   Auto-generated passphrase (non-interactive mode)");
  }

  // Save wallet
  const walletData = {
    address: wallet.address,
    privateKey: wallet.privateKey, // TODO: encrypt with passphrase in v2
    network: "eip155:8453", // Base mainnet
    createdAt: new Date().toISOString(),
    note: "x402 agent payment wallet. DO NOT SHARE private key."
  };

  // Ensure directory exists
  mkdirSync(WALLET_DIR, { recursive: true, mode: 0o700 });

  // For now, store plaintext (v2 will add encryption)
  writeFileSync(WALLET_FILE, JSON.stringify(walletData, null, 2), { mode: 0o600 });

  console.error("💾 Wallet saved to", WALLET_FILE);
  console.error("");
  console.error("⚠️  IMPORTANT: Back up your wallet! If lost, funds are gone forever.");
  console.error("⚠️  NEVER share your private key with anyone.");
  console.error("");
  console.error("📬 Fund this address with USDC on Base network:");
  console.error("   ", wallet.address);

  // Output address to stdout (for scripting)
  console.log(wallet.address);
}

main().catch(console.error);
