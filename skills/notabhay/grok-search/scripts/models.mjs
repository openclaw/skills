#!/usr/bin/env node
/**
 * models.mjs
 *
 * List available xAI models.
 *
 * Examples:
 *   node {baseDir}/scripts/models.mjs
 *   node {baseDir}/scripts/models.mjs --json
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function usage(msg) {
  if (msg) console.error(msg);
  console.error("Usage: models.mjs [--json] [--raw]");
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

const args = process.argv.slice(2);
let jsonOut = false;
let rawOut = false;
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--json") jsonOut = true;
  else if (a === "--raw") rawOut = true;
  else if (a.startsWith("-")) usage(`Unknown flag: ${a}`);
}

const apiKey = readKeyFromClawdbotConfig();
if (!apiKey) {
  console.error("Missing XAI_API_KEY.");
  process.exit(1);
}

async function fetchJson(url) {
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
  });
  const t = await res.text();
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${t.slice(0, 400)}`);
  return JSON.parse(t);
}

let data;
try {
  data = await fetchJson("https://api.x.ai/v1/language-models");
} catch {
  data = await fetchJson("https://api.x.ai/v1/models");
}

if (jsonOut) {
  console.log(JSON.stringify(data, null, 2));
  process.exit(0);
}

const rows = [];
if (Array.isArray(data?.data)) {
  for (const m of data.data) rows.push({ id: m.id, owned_by: m.owned_by, object: m.object });
} else if (Array.isArray(data)) {
  for (const m of data) rows.push({ id: m.id, owned_by: m.owned_by, object: m.object });
} else if (Array.isArray(data?.models)) {
  for (const m of data.models) rows.push({ id: m.id ?? m.model ?? m.name, owned_by: m.owned_by, object: m.object });
}

rows.sort((a, b) => String(a.id).localeCompare(String(b.id)));
for (const r of rows) console.log(r.id);

if (rawOut) {
  console.error("\n--- RAW ---\n");
  console.error(JSON.stringify(data, null, 2));
}
