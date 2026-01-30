#!/usr/bin/env node
/**
 * x402 Wallet Balance Checker
 * Shows USDC balance on Base mainnet and testnet
 */
import { ethers } from "ethers";
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const WALLET_FILE = join(homedir(), ".x402", "wallet.json");

// USDC contract addresses
const USDC = {
  "base-mainnet": {
    rpc: "https://mainnet.base.org",
    contract: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    chainId: 8453,
  },
  "base-sepolia": {
    rpc: "https://sepolia.base.org",
    contract: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    chainId: 84532,
  },
};

// Minimal ERC20 ABI for balanceOf
const ERC20_ABI = ["function balanceOf(address) view returns (uint256)"];

async function getBalance(network, address) {
  const config = USDC[network];
  const provider = new ethers.JsonRpcProvider(config.rpc);
  const usdc = new ethers.Contract(config.contract, ERC20_ABI, provider);
  const balance = await usdc.balanceOf(address);
  return ethers.formatUnits(balance, 6); // USDC has 6 decimals
}

async function main() {
  if (!existsSync(WALLET_FILE)) {
    console.error("❌ No wallet found. Run setup.sh first.");
    process.exit(1);
  }

  const wallet = JSON.parse(readFileSync(WALLET_FILE, "utf-8"));

  console.log(`👛 Balance for ${wallet.address}`);
  console.log("=".repeat(50));

  try {
    const mainnetBalance = await getBalance("base-mainnet", wallet.address);
    console.log(`   Base Mainnet:  $${mainnetBalance} USDC`);
  } catch (e) {
    console.log(`   Base Mainnet:  ⚠️ Error: ${e.message}`);
  }

  try {
    const testnetBalance = await getBalance("base-sepolia", wallet.address);
    console.log(`   Base Sepolia:  $${testnetBalance} USDC (testnet)`);
  } catch (e) {
    console.log(`   Base Sepolia:  ⚠️ Error: ${e.message}`);
  }

  // Also check ETH for gas
  try {
    const provider = new ethers.JsonRpcProvider("https://mainnet.base.org");
    const ethBalance = await provider.getBalance(wallet.address);
    console.log(`   Base ETH:      ${ethers.formatEther(ethBalance)} ETH (for gas)`);
  } catch (e) {
    // ignore
  }
}

main().catch(console.error);
