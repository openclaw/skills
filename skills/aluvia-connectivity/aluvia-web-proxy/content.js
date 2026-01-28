#!/usr/bin/env node

import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";
import { AluviaClient } from "@aluvia/sdk";

const url = process.argv[2];

if (!url) {
  console.log("Usage: content.js <url>");
  console.log("\nExtracts readable content from a webpage as markdown.");
  console.log("\nExamples:");
  console.log("  content.js https://example.com/article");
  console.log(
    "  content.js https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html",
  );
  process.exit(1);
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
    const response = await proxyFetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
      },
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      console.error(`HTTP ${response.status}: ${response.statusText}`);
      await connection.close();
      process.exit(1);
    }

    const html = await response.text();
    const dom = new JSDOM(html, { url });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    if (article && article.content) {
      if (article.title) {
        console.log(`# ${article.title}\n`);
      }
      console.log(htmlToMarkdown(article.content));
      await connection.close();
      process.exit(0);
    }

    // Fallback: try to extract main content
    const fallbackDoc = new JSDOM(html, { url });
    const body = fallbackDoc.window.document;
    body
      .querySelectorAll("script, style, noscript, nav, header, footer, aside")
      .forEach((el) => el.remove());

    const title = body.querySelector("title")?.textContent?.trim();
    const main =
      body.querySelector("main, article, [role='main'], .content, #content") ||
      body.body;

    if (title) {
      console.log(`# ${title}\n`);
    }

    const text = main?.innerHTML || "";
    if (text.trim().length > 100) {
      console.log(htmlToMarkdown(text));
    } else {
      console.error("Could not extract readable content from this page.");
      await connection.close();
      process.exit(1);
    }
    await connection.close();
    process.exit(0);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
})();
