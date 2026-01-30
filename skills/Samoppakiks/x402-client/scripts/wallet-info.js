#!/usr/bin/env node
/**
 * x402 Wallet Info
 * Display wallet address and optionally export private key
 */
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const WALLET_FILE = join(homedir(), ".x402", "wallet.json");

function main() {
  if (!existsSync(WALLET_FILE)) {
    console.error("❌ No wallet found. Run setup.sh first.");
    process.exit(1);
  }

  const wallet = JSON.parse(readFileSync(WALLET_FILE, "utf-8"));

  console.log("👛 x402 Wallet");
  console.log("==============");
  console.log(`Address:  ${wallet.address}`);
  console.log(`Network:  Base (${wallet.network})`);
  console.log(`Created:  ${wallet.createdAt}`);

  if (process.argv.includes("--export-key")) {
    console.log("");
    console.log("⚠️  PRIVATE KEY (NEVER SHARE):");
    console.log(`   ${wallet.privateKey}`);
  } else {
    console.log("");
    console.log("Use --export-key to show private key (dangerous)");
  }
}

main();
