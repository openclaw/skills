#!/usr/bin/env node

import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";
import { AluviaClient } from "@aluvia/sdk";

const args = process.argv.slice(2);

const contentIndex = args.indexOf("--content");
const fetchContent = contentIndex !== -1;
if (fetchContent) args.splice(contentIndex, 1);

let numResults = 5;
const nIndex = args.indexOf("-n");
if (nIndex !== -1 && args[nIndex + 1]) {
  numResults = parseInt(args[nIndex + 1], 10);
  args.splice(nIndex, 2);
}

const query = args.join(" ");

if (!query) {
  console.log("Usage: search.js <query> [-n <num>] [--content]");
  console.log("\nOptions:");
  console.log("  -n <num>    Number of results (default: 5)");
  console.log("  --content   Fetch readable content as markdown");
  console.log("\nExamples:");
  console.log('  search.js "javascript async await"');
  console.log('  search.js "rust programming" -n 10');
  console.log('  search.js "climate change" --content');
  process.exit(1);
}

async function fetchBraveResults(query, numResults, proxyFetch) {
  const url = `https://search.brave.com/search?q=${encodeURIComponent(query)}`;
  const BRAVE_API_KEY = process.env.BRAVE_API_KEY;
  if (!BRAVE_API_KEY) {
    throw new Error("Missing BRAVE_API_KEY environment variable.");
  }
  const response = await proxyFetch(url, {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
      Accept:
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
      "sec-ch-ua":
        '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"macOS"',
      "sec-fetch-dest": "document",
      "sec-fetch-mode": "navigate",
      "sec-fetch-site": "none",
      "sec-fetch-user": "?1",
      "x-brave-key": BRAVE_API_KEY,
    },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  const html = await response.text();
  const dom = new JSDOM(html);
  const doc = dom.window.document;
  const results = [];
  // Find all search result snippets with data-type="web"
  const snippets = doc.querySelectorAll('div.snippet[data-type="web"]');
  for (const snippet of snippets) {
    if (results.length >= numResults) break;
    // Get the main link and title
    const titleLink = snippet.querySelector("a.svelte-14r20fy");
    if (!titleLink) continue;
    const link = titleLink.getAttribute("href");
    if (!link || link.includes("brave.com")) continue;
    const titleEl = titleLink.querySelector(".title");
    const title =
      titleEl?.textContent?.trim() || titleLink.textContent?.trim() || "";
    // Get the snippet/description
    const descEl = snippet.querySelector(".generic-snippet .content");
    let snippetText = descEl?.textContent?.trim() || "";
    // Remove date prefix if present
    snippetText = snippetText.replace(/^[A-Z][a-z]+ \d+, \d{4} -\s*/, "");
    if (title && link) {
      results.push({ title, link, snippet: snippetText });
    }
  }
  return results;
}

function htmlToMarkdown(html) {
  const turndown = new TurndownService({
    headingStyle: "atx",
    codeBlockStyle: "fenced",
  });
  turndown.use(gfm);
  turndown.addRule("removeEmptyLinks", {
    filter: (node) => node.nodeName === "A" && !node.textContent?.trim(),
    replacement: () => "",
  });
  return turndown
    .turndown(html)
    .replace(/\[\\?\[\s*\\?\]\]\([^)]*\)/g, "")
    .replace(/ +/g, " ")
    .replace(/\s+,/g, ",")
    .replace(/\s+\./g, ".")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

async function fetchPageContent(url, proxyFetch) {
  try {
    const response = await proxyFetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok) {
      return `(HTTP ${response.status})`;
    }
    const html = await response.text();
    const dom = new JSDOM(html, { url });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();
    if (article && article.content) {
      return htmlToMarkdown(article.content).substring(0, 5000);
    }
    // Fallback: try to get main content
    const fallbackDoc = new JSDOM(html, { url });
    const body = fallbackDoc.window.document;
    body
      .querySelectorAll("script, style, noscript, nav, header, footer, aside")
      .forEach((el) => el.remove());
    const main =
      body.querySelector("main, article, [role='main'], .content, #content") ||
      body.body;
    const text = main?.textContent || "";
    if (text.trim().length > 100) {
      return text.trim().substring(0, 5000);
    }
    return "(Could not extract content)";
  } catch (e) {
    return `(Error: ${e.message})`;
  }
}

(async () => {
  const ALUVIA_API_KEY = process.env.ALUVIA_API_KEY;
  if (!ALUVIA_API_KEY) {
    console.error("Missing ALUVIA_API_KEY environment variable.");
    process.exit(1);
  }

  const clientOpts = { apiKey: ALUVIA_API_KEY };
  const ALUVIA_CONNECTION_ID = process.env.ALUVIA_CONNECTION_ID;
  if (ALUVIA_CONNECTION_ID) {
    clientOpts.connectionId = isNaN(Number(ALUVIA_CONNECTION_ID))
      ? ALUVIA_CONNECTION_ID
      : Number(ALUVIA_CONNECTION_ID);
  }

  const client = new AluviaClient(clientOpts);
  const connection = await client.start();
  const proxyFetch = connection.asUndiciFetch();

  try {
    const results = await fetchBraveResults(query, numResults, proxyFetch);
    if (results.length === 0) {
      console.error("No results found.");
      await connection.close();
      process.exit(0);
    }
    if (fetchContent) {
      for (const result of results) {
        result.content = await fetchPageContent(result.link, proxyFetch);
      }
    }
    for (let i = 0; i < results.length; i++) {
      const r = results[i];
      console.log(`--- Result ${i + 1} ---`);
      console.log(`Title: ${r.title}`);
      console.log(`Link: ${r.link}`);
      console.log(`Snippet: ${r.snippet}`);
      if (r.content) {
        console.log(`Content:\n${r.content}`);
      }
      console.log("");
    }
    await connection.close();
    process.exit(0);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
})();
