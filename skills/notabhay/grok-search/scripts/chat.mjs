#!/usr/bin/env node
/**
 * chat.mjs
 *
 * Chat with xAI Grok via Responses API.
 * Supports optional image attachments.
 *
 * Examples:
 *   node {baseDir}/scripts/chat.mjs "What is xAI?"
 *   node {baseDir}/scripts/chat.mjs --model grok-4-1-fast "Summarize today's AI news"
 *   node {baseDir}/scripts/chat.mjs --image ./pic.jpg "What's in this image?"
 *   node {baseDir}/scripts/chat.mjs --json "Return a JSON object with keys a,b"
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function usage(msg) {
  if (msg) console.error(msg);
  console.error(
    "Usage: chat.mjs [--model <id>] [--json] [--raw] [--image <path>]... <prompt>"
  );
  process.exit(2);
}

function readKeyFromClawdbotConfig() {
  try {
    const p = path.join(os.homedir(), ".clawdbot", "clawdbot.json");
    const raw = fs.readFileSync(p, "utf8");
    const j = JSON.parse(raw);

    return (
      process.env.XAI_API_KEY ||
      j?.env?.XAI_API_KEY ||
      j?.env?.vars?.XAI_API_KEY ||
      j?.skills?.entries?.["grok-search"]?.apiKey ||
      j?.skills?.entries?.xai?.apiKey ||
      null
    );
  } catch {
    return process.env.XAI_API_KEY || null;
  }
}

function mimeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".png") return "image/png";
  if (ext === ".webp") return "image/webp";
  if (ext === ".gif") return "image/gif";
  return null;
}

function toDataUrl(filePath) {
  const mime = mimeFor(filePath);
  if (!mime) throw new Error(`Unsupported image type: ${filePath}`);
  const buf = fs.readFileSync(filePath);
  return `data:${mime};base64,${buf.toString("base64")}`;
}

function collectCitations(resp) {
  const out = new Set();
  if (Array.isArray(resp?.citations)) {
    for (const u of resp.citations) if (typeof u === "string" && u) out.add(u);
  }
  if (Array.isArray(resp?.output)) {
    for (const item of resp.output) {
      const content = Array.isArray(item?.content) ? item.content : [];
      for (const c of content) {
        const ann = Array.isArray(c?.annotations) ? c.annotations : [];
        for (const a of ann) {
          const url = a?.url || a?.web_citation?.url;
          if (typeof url === "string" && url) out.add(url);
        }
      }
    }
  }
  return [...out];
}

const args = process.argv.slice(2);
if (!args.length) usage();

let model = process.env.GROK_MODEL || "grok-4-1-fast";
let jsonOut = false;
let rawOut = false;
let images = [];
let promptParts = [];

for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--model") {
    const v = args[++i];
    if (!v) usage("Missing value for --model");
    model = v;
  } else if (a === "--json") jsonOut = true;
  else if (a === "--raw") rawOut = true;
  else if (a === "--image") {
    const v = args[++i];
    if (!v) usage("Missing value for --image");
    images.push(v);
  } else if (a.startsWith("-")) usage(`Unknown flag: ${a}`);
  else promptParts.push(a);
}

const prompt = promptParts.join(" ").trim();
if (!prompt) usage("Missing <prompt>");

const apiKey = readKeyFromClawdbotConfig();
if (!apiKey) {
  console.error("Missing XAI_API_KEY.");
  process.exit(1);
}

const content = [{ type: "input_text", text: prompt }];
for (const img of images) {
  content.push({ type: "input_image", image_url: toDataUrl(img) });
}

const body = {
  model,
  input: [{ role: "user", content }],
  store: false,
};

const res = await fetch("https://api.x.ai/v1/responses", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
  body: JSON.stringify(body),
});

if (!res.ok) {
  const t = await res.text().catch(() => "");
  console.error(`xAI API error: ${res.status} ${res.statusText}`);
  console.error(t.slice(0, 4000));
  process.exit(1);
}

const data = await res.json();
const text =
  data.output_text ||
  data?.output
    ?.flatMap((o) => (Array.isArray(o?.content) ? o.content : []))
    ?.find((c) => c?.type === "output_text" && typeof c?.text === "string")
    ?.text ||
  "";

if (jsonOut) {
  console.log(JSON.stringify({ model, prompt, text, citations: collectCitations(data) }, null, 2));
  if (rawOut) console.error(JSON.stringify(data, null, 2));
  process.exit(0);
}

console.log(text.trim());
const cites = collectCitations(data);
if (cites.length) {
  console.log("\nCitations:");
  for (const c of cites) console.log(`- ${c}`);
}

if (rawOut) {
  console.error("\n--- RAW RESPONSE (debug) ---\n");
  console.error(JSON.stringify(data, null, 2));
}
