#!/usr/bin/env tsx

/**
 * OnChat CLI — Read, write, and engage with on-chain chat on Base L2.
 *
 * This script provides a complete interface for AI agents (or humans) to
 * interact with the OnChat protocol directly from the command line.
 *
 * Read operations work without any setup. For write operations (send, join),
 * set the ONCHAT_PRIVATE_KEY environment variable with a wallet private key
 * that has ETH on Base.
 *
 * Usage: npx tsx onchat.ts <command> [options]
 *
 * @see https://github.com/sebayaki/onchat
 * @see https://onchat.sebayaki.com
 */

import {
  createPublicClient,
  createWalletClient,
  http,
  fallback,
  formatEther,
  type PublicClient,
  type WalletClient,
  type Address,
  type Hex,
} from "viem";
import { base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";

// ─── Contract ────────────────────────────────────────────────────────────────

const ONCHAT_ADDRESS = "0x898D291C2160A9CB110398e9dF3693b7f2c4af2D" as const;

const ONCHAT_ABI = [
  // Read Functions
  { type: "function", name: "channelCreationFee", inputs: [], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "messageFeeBase", inputs: [], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "messageFeePerChar", inputs: [], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "getChannelCount", inputs: [], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "getChannel", inputs: [{ name: "slugHash", type: "bytes32" }], outputs: [{ name: "info", type: "tuple", components: [{ name: "slugHash", type: "bytes32" }, { name: "slug", type: "string" }, { name: "owner", type: "address" }, { name: "createdAt", type: "uint40" }, { name: "memberCount", type: "uint256" }, { name: "messageCount", type: "uint256" }] }], stateMutability: "view" },
  { type: "function", name: "getLatestChannels", inputs: [{ name: "offset", type: "uint256" }, { name: "limit", type: "uint256" }], outputs: [{ name: "channels", type: "tuple[]", components: [{ name: "slugHash", type: "bytes32" }, { name: "slug", type: "string" }, { name: "owner", type: "address" }, { name: "createdAt", type: "uint40" }, { name: "memberCount", type: "uint256" }, { name: "messageCount", type: "uint256" }] }], stateMutability: "view" },
  { type: "function", name: "getMessageCount", inputs: [{ name: "slugHash", type: "bytes32" }], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "getLatestMessages", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "offset", type: "uint256" }, { name: "limit", type: "uint256" }], outputs: [{ name: "messages", type: "tuple[]", components: [{ name: "sender", type: "address" }, { name: "timestamp", type: "uint40" }, { name: "isHidden", type: "bool" }, { name: "content", type: "string" }] }], stateMutability: "view" },
  { type: "function", name: "getMessagesRange", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "startIndex", type: "uint256" }, { name: "endIndex", type: "uint256" }], outputs: [{ name: "messages", type: "tuple[]", components: [{ name: "sender", type: "address" }, { name: "timestamp", type: "uint40" }, { name: "isHidden", type: "bool" }, { name: "content", type: "string" }] }], stateMutability: "view" },
  { type: "function", name: "getChannelMembers", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "offset", type: "uint256" }, { name: "limit", type: "uint256" }], outputs: [{ name: "members", type: "address[]" }], stateMutability: "view" },
  { type: "function", name: "getUserChannels", inputs: [{ name: "user", type: "address" }, { name: "offset", type: "uint256" }, { name: "limit", type: "uint256" }], outputs: [{ name: "slugHashes", type: "bytes32[]" }], stateMutability: "view" },
  { type: "function", name: "getUserChannelCount", inputs: [{ name: "user", type: "address" }], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "isMember", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "user", type: "address" }], outputs: [{ name: "", type: "bool" }], stateMutability: "view" },
  { type: "function", name: "isModerator", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "user", type: "address" }], outputs: [{ name: "", type: "bool" }], stateMutability: "view" },
  { type: "function", name: "calculateMessageFee", inputs: [{ name: "contentLength", type: "uint256" }], outputs: [{ name: "fee", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "computeSlugHash", inputs: [{ name: "slug", type: "string" }], outputs: [{ name: "", type: "bytes32" }], stateMutability: "pure" },
  { type: "function", name: "getSlug", inputs: [{ name: "slugHash", type: "bytes32" }], outputs: [{ name: "", type: "string" }], stateMutability: "view" },
  { type: "function", name: "ownerBalances", inputs: [{ name: "owner", type: "address" }], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "treasuryBalance", inputs: [], outputs: [{ name: "", type: "uint256" }], stateMutability: "view" },
  // Write Functions
  { type: "function", name: "createChannel", inputs: [{ name: "slug", type: "string" }], outputs: [{ name: "slugHash", type: "bytes32" }], stateMutability: "payable" },
  { type: "function", name: "joinChannel", inputs: [{ name: "slugHash", type: "bytes32" }], outputs: [], stateMutability: "nonpayable" },
  { type: "function", name: "leaveChannel", inputs: [{ name: "slugHash", type: "bytes32" }], outputs: [], stateMutability: "nonpayable" },
  { type: "function", name: "sendMessage", inputs: [{ name: "slugHash", type: "bytes32" }, { name: "content", type: "string" }], outputs: [], stateMutability: "payable" },
  { type: "function", name: "claimOwnerBalance", inputs: [], outputs: [], stateMutability: "nonpayable" },
] as const;

// ─── RPC & Clients ───────────────────────────────────────────────────────────

const RPC_URLS = [
  "https://base-rpc.publicnode.com",
  "https://mainnet.base.org",
  "https://base-mainnet.public.blastapi.io",
  "https://1rpc.io/base",
  "https://base.drpc.org",
];

function getPublicClient(): PublicClient {
  return createPublicClient({
    chain: base,
    transport: fallback(RPC_URLS.map((url) => http(url, { timeout: 10_000 }))),
  }) as PublicClient;
}

function getWalletClient(): WalletClient {
  const key = process.env.ONCHAT_PRIVATE_KEY;
  if (!key) {
    console.error("Error: ONCHAT_PRIVATE_KEY environment variable is required for write operations.");
    process.exit(1);
  }
  const privateKey = (key.startsWith("0x") ? key : `0x${key}`) as Hex;
  const account = privateKeyToAccount(privateKey);
  return createWalletClient({
    account,
    chain: base,
    transport: fallback(RPC_URLS.map((url) => http(url, { timeout: 10_000 }))),
  });
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function shortAddr(addr: string): string {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

function relativeTime(timestamp: number): string {
  const now = Math.floor(Date.now() / 1000);
  const diff = now - timestamp;
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
  if (diff < 31536000) return `${Math.floor(diff / 2592000)}mo ago`;
  return `${Math.floor(diff / 31536000)}y ago`;
}

function parseArgs(args: string[]): { positional: string[]; flags: Record<string, string> } {
  const positional: string[] = [];
  const flags: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith("--")) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = "true";
      }
    } else {
      positional.push(args[i]);
    }
  }
  return { positional, flags };
}

// ─── Commands ────────────────────────────────────────────────────────────────

async function cmdChannels(limit: number) {
  const client = getPublicClient();

  const totalCount = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getChannelCount",
  });

  const fetchLimit = Math.min(Number(totalCount), Math.max(limit, 50));

  const channels = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getLatestChannels",
    args: [BigInt(0), BigInt(fetchLimit)],
  });

  const sorted = [...channels].sort((a, b) => Number(b.messageCount - a.messageCount));
  const display = sorted.slice(0, limit);

  console.log(`📢 OnChat Channels (top ${display.length} of ${totalCount} total)\n`);
  console.log("Channel".padEnd(30) + "Messages".padEnd(12) + "Members".padEnd(12) + "Owner");
  console.log("─".repeat(78));

  for (const ch of display) {
    const slug = `#${ch.slug}`;
    console.log(
      slug.padEnd(30) +
      String(ch.messageCount).padEnd(12) +
      String(ch.memberCount).padEnd(12) +
      shortAddr(ch.owner)
    );
  }
}

async function cmdRead(slug: string, limit: number) {
  const client = getPublicClient();

  const slugHash = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "computeSlugHash",
    args: [slug],
  });

  const channel = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getChannel",
    args: [slugHash],
  });

  if (!channel.slug) {
    console.error(`Error: Channel #${slug} not found.`);
    process.exit(1);
  }

  const messages = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getLatestMessages",
    args: [slugHash, BigInt(0), BigInt(limit)],
  });

  console.log(`💬 #${slug} — ${channel.messageCount} messages, ${channel.memberCount} members\n`);

  if (messages.length === 0) {
    console.log("(no messages yet)");
    return;
  }

  // Messages come latest-first, reverse to show chronological order
  const chronological = [...messages].reverse();
  const totalCount = Number(channel.messageCount);
  const startId = totalCount - chronological.length;

  for (let i = 0; i < chronological.length; i++) {
    const msg = chronological[i];
    const msgId = startId + i;
    if (msg.isHidden) {
      console.log(`#${msgId} [${relativeTime(Number(msg.timestamp))}] ${shortAddr(msg.sender)}: [hidden]`);
    } else {
      console.log(`#${msgId} [${relativeTime(Number(msg.timestamp))}] ${shortAddr(msg.sender)}: ${msg.content}`);
    }
  }
}

async function cmdInfo(slug: string) {
  const client = getPublicClient();

  const slugHash = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "computeSlugHash",
    args: [slug],
  });

  const channel = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getChannel",
    args: [slugHash],
  });

  if (!channel.slug) {
    console.error(`Error: Channel #${slug} not found.`);
    process.exit(1);
  }

  const createdDate = new Date(Number(channel.createdAt) * 1000);

  console.log(`ℹ️  Channel Info: #${channel.slug}`);
  console.log(`   Slug Hash:     ${channel.slugHash}`);
  console.log(`   Owner:         ${channel.owner}`);
  console.log(`   Created:       ${createdDate.toISOString()} (${relativeTime(Number(channel.createdAt))})`);
  console.log(`   Members:       ${channel.memberCount}`);
  console.log(`   Messages:      ${channel.messageCount}`);
}

async function cmdFee(message: string) {
  const client = getPublicClient();
  const contentLength = BigInt(new TextEncoder().encode(message).length);

  const fee = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "calculateMessageFee",
    args: [contentLength],
  });

  console.log(`💰 Message Fee`);
  console.log(`   Message:    "${message}"`);
  console.log(`   Length:     ${contentLength} bytes`);
  console.log(`   Fee:        ${formatEther(fee)} ETH`);
}

async function cmdBalance() {
  const wallet = getWalletClient();
  const client = getPublicClient();
  const address = wallet.account!.address;

  const balance = await client.getBalance({ address });

  console.log(`💳 Wallet Balance`);
  console.log(`   Address:    ${address}`);
  console.log(`   Balance:    ${formatEther(balance)} ETH (Base)`);
}

async function cmdJoin(slug: string) {
  const client = getPublicClient();
  const wallet = getWalletClient();
  const address = wallet.account!.address;

  const slugHash = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "computeSlugHash",
    args: [slug],
  });

  const channel = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getChannel",
    args: [slugHash],
  });

  if (!channel.slug) {
    console.error(`Error: Channel #${slug} not found.`);
    process.exit(1);
  }

  const already = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "isMember",
    args: [slugHash, address],
  });

  if (already) {
    console.log(`✅ Already a member of #${slug}`);
    return;
  }

  console.log(`Joining #${slug}...`);

  const hash = await wallet.writeContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "joinChannel",
    args: [slugHash],
    chain: base,
  });

  console.log(`⏳ Transaction sent: ${hash}`);
  const receipt = await client.waitForTransactionReceipt({ hash });
  if (receipt.status === "success") {
    console.log(`✅ Joined #${slug} successfully!`);
  } else {
    console.error(`❌ Transaction failed.`);
    process.exit(1);
  }
}

async function cmdSend(slug: string, message: string) {
  const client = getPublicClient();
  const wallet = getWalletClient();
  const address = wallet.account!.address;

  const slugHash = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "computeSlugHash",
    args: [slug],
  });

  const channel = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "getChannel",
    args: [slugHash],
  });

  if (!channel.slug) {
    console.error(`Error: Channel #${slug} not found.`);
    process.exit(1);
  }

  // Auto-join if not a member
  const isMemberResult = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "isMember",
    args: [slugHash, address],
  });

  if (!isMemberResult) {
    console.log(`Not a member of #${slug}, joining first...`);
    const joinHash = await wallet.writeContract({
      address: ONCHAT_ADDRESS,
      abi: ONCHAT_ABI,
      functionName: "joinChannel",
      args: [slugHash],
      chain: base,
    });
    const joinReceipt = await client.waitForTransactionReceipt({ hash: joinHash });
    if (joinReceipt.status !== "success") {
      console.error(`❌ Failed to join channel.`);
      process.exit(1);
    }
    console.log(`✅ Joined #${slug}`);
  }

  // Calculate fee
  const contentLength = BigInt(new TextEncoder().encode(message).length);
  const fee = await client.readContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "calculateMessageFee",
    args: [contentLength],
  });

  // Check balance
  const balance = await client.getBalance({ address });
  if (balance < fee) {
    console.error(`❌ Insufficient balance. Need ${formatEther(fee)} ETH, have ${formatEther(balance)} ETH.`);
    process.exit(1);
  }

  console.log(`Sending message to #${slug} (fee: ${formatEther(fee)} ETH)...`);

  const hash = await wallet.writeContract({
    address: ONCHAT_ADDRESS,
    abi: ONCHAT_ABI,
    functionName: "sendMessage",
    args: [slugHash, message],
    value: fee,
    chain: base,
  });

  console.log(`⏳ Transaction sent: ${hash}`);
  const receipt = await client.waitForTransactionReceipt({ hash });
  if (receipt.status === "success") {
    console.log(`✅ Message sent to #${slug}!`);
  } else {
    console.error(`❌ Transaction failed.`);
    process.exit(1);
  }
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    printUsage();
    process.exit(1);
  }

  const command = args[0];
  const { positional, flags } = parseArgs(args.slice(1));
  const limit = flags.limit ? parseInt(flags.limit, 10) : 20;

  try {
    switch (command) {
      case "channels":
        await cmdChannels(limit);
        break;

      case "read": {
        const slug = positional[0];
        if (!slug) {
          console.error("Usage: onchat.ts read <channel-slug> [--limit N]");
          process.exit(1);
        }
        await cmdRead(slug, limit);
        break;
      }

      case "info": {
        const slug = positional[0];
        if (!slug) {
          console.error("Usage: onchat.ts info <channel-slug>");
          process.exit(1);
        }
        await cmdInfo(slug);
        break;
      }

      case "fee": {
        const message = positional[0];
        if (!message) {
          console.error("Usage: onchat.ts fee \"<message>\"");
          process.exit(1);
        }
        await cmdFee(message);
        break;
      }

      case "balance":
        await cmdBalance();
        break;

      case "join": {
        const slug = positional[0];
        if (!slug) {
          console.error("Usage: onchat.ts join <channel-slug>");
          process.exit(1);
        }
        await cmdJoin(slug);
        break;
      }

      case "send": {
        const slug = positional[0];
        const message = positional[1];
        if (!slug || !message) {
          console.error('Usage: onchat.ts send <channel-slug> "<message>"');
          process.exit(1);
        }
        await cmdSend(slug, message);
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        printUsage();
        process.exit(1);
    }
  } catch (err: any) {
    if (err.shortMessage) {
      console.error(`Error: ${err.shortMessage}`);
    } else if (err.message) {
      console.error(`Error: ${err.message}`);
    } else {
      console.error("Error:", err);
    }
    process.exit(1);
  }
}

function printUsage() {
  console.log(`OnChat CLI — On-chain chat on Base L2

Usage: npx tsx onchat.ts <command> [options]

Commands:
  channels [--limit N]              List channels sorted by message count
  read <channel-slug> [--limit N]   Read latest messages from a channel
  send <channel-slug> "<message>"   Send a message (needs ONCHAT_PRIVATE_KEY)
  join <channel-slug>               Join a channel (needs ONCHAT_PRIVATE_KEY)
  info <channel-slug>               Get channel info
  balance                           Check wallet ETH balance
  fee "<message>"                   Calculate message fee

Environment:
  ONCHAT_PRIVATE_KEY               Wallet private key for on-chain operations`);
}

main();
