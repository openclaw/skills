#!/usr/bin/env tsx
/**
 * Context7 Query CLI
 *
 * Query Context7 API to search documentation and repository code.
 *
 * Usage:
 *   Search:   npx tsx query.ts search <repo_owner/repo_name> <search_query>
 *   Context:  npx tsx query.ts context <repo_owner/repo_name> <search_query>
 *
 * Examples:
 *   npx tsx query.ts search "better-auth/better-auth" "signIn social redirect callback"
 *   npx tsx query.ts context "facebook/react" "useState hook"
 */

import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// Load API key from .env file in the same directory as this script
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = join(__dirname, ".env");
let API_KEY = process.env.CONTEXT7_API_KEY;

// Try to load from .env file if not in environment
if (!API_KEY) {
  try {
    const envContent = readFileSync(envPath, "utf-8");
    const match = envContent.match(/CONTEXT7_API_KEY=(.+)/);
    API_KEY = match?.[1]?.trim();
  } catch {
    // .env file doesn't exist, continue with null
  }
}

if (!API_KEY) {
  console.error("Error: CONTEXT7_API_KEY not found");
  console.error("Set it in environment or in .env file in this directory");
  process.exit(1);
}

const command = process.argv[2];
const repoName = process.argv[3];
const query = process.argv[4];

// Help text
if (!command || command === "--help" || command === "-h") {
  console.log(`
Context7 Query CLI

Usage:
  npx tsx query.ts <command> <repo_owner/repo_name> <search_query>

Commands:
  search   Search for libraries by name with intelligent LLM-powered ranking
  context  Retrieve intelligent, LLM-reranked documentation context

Examples:
  npx tsx query.ts search "nextjs" "setup ssr"
  npx tsx query.ts context "better-auth/better-auth" "signIn social redirect"

For more info: https://context7.com/docs
`);
  process.exit(0);
}

if (!repoName || !query) {
  console.error("Error: Missing arguments");
  console.error("Usage:");
  console.error("  Search:   npx tsx query.ts search <repo> <query>");
  console.error("  Context:  npx tsx query.ts context <repo> <query>");
  process.exit(1);
}

// Ensure repo name starts with /
const libraryId = repoName.startsWith("/") ? repoName : `/${repoName}`;

async function searchLibraries() {
  try {
    console.log(`Searching Context7 for libraries matching "${query}"...`);

    // Context7 Search API
    const url = new URL("https://context7.com/api/v2/libs/search");
    url.searchParams.set("libraryName", libraryId.split("/")[1] || "");
    url.searchParams.set("query", query);

    const response = await fetch(url.toString(), {
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`Context7 API error (${response.status}):`, error);
      process.exit(1);
    }

    const data = await response.json();
    
    console.log("\n=== Search Results ===\n");
    
    if (Array.isArray(data) && data.length > 0) {
      data.forEach((lib: any, i: number) => {
        console.log(`${i + 1}. ${lib.name || lib.id}`);
        console.log(`   Trust Score: ${lib.trustScore || "N/A"}`);
        console.log(`   Benchmark: ${lib.benchmarkScore || "N/A"}`);
        if (lib.versions) {
          console.log(`   Versions: ${lib.versions.slice(0, 5).join(", ")}${lib.versions.length > 5 ? "..." : ""}`);
        }
        console.log("");
      });
    } else {
      console.log("No results found.");
    }
  } catch (error: any) {
    console.error("Error searching Context7:", error.message);
    process.exit(1);
  }
}

async function getContext() {
  try {
    console.log(`Getting context for: "${query}" in ${libraryId}...`);

    // Context7 REST API
    const url = new URL("https://context7.com/api/v2/context");
    url.searchParams.set("libraryId", libraryId);
    url.searchParams.set("query", query);
    url.searchParams.set("type", "txt");

    const response = await fetch(url.toString(), {
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`Context7 API error (${response.status}):`, error);
      process.exit(1);
    }

    const text = await response.text();
    console.log("\n=== Context Results ===\n");
    console.log(text);
  } catch (error: any) {
    console.error("Error querying Context7:", error.message);
    process.exit(1);
  }
}

if (command === "search" || command === "s") {
  searchLibraries();
} else if (command === "context" || command === "c") {
  getContext();
} else {
  console.error(`Unknown command: ${command}`);
  console.error("Use 'search' or 'context'");
  process.exit(1);
}
