import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";
import { execSync } from "child_process";

// depcheck doesn't have great types, require it
const depcheck = require("depcheck");

export interface AuditResult {
  unused: string[];
  unusedDev: string[];
  missing: Record<string, string[]>;
  outdated: string[];
  analysis: string;
}

export async function runDepcheck(dir: string): Promise<{ unused: string[]; unusedDev: string[]; missing: Record<string, string[]> }> {
  return new Promise((resolve, reject) => {
    const options = {
      ignoreDirs: ["dist", "build", ".next", "node_modules"],
      ignoreMatches: ["typescript", "@types/*"],
    };

    depcheck(dir, options, (results: any) => {
      resolve({
        unused: results.dependencies || [],
        unusedDev: results.devDependencies || [],
        missing: results.missing || {},
      });
    });
  });
}

export async function checkOutdated(dir: string): Promise<string[]> {
  try {
    const output = execSync("npm outdated --json 2>/dev/null || true", { cwd: dir, encoding: "utf-8" });
    if (!output.trim()) return [];
    const parsed = JSON.parse(output);
    return Object.keys(parsed);
  } catch {
    return [];
  }
}

export async function analyzeResults(depcheckResult: { unused: string[]; unusedDev: string[]; missing: Record<string, string[]> }, outdated: string[], pkgJson: any): Promise<string> {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("Missing OPENAI_API_KEY environment variable. Set it with: export OPENAI_API_KEY=sk-...");
  }

  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const context = {
    projectName: pkgJson.name || "unknown",
    dependencies: Object.keys(pkgJson.dependencies || {}),
    devDependencies: Object.keys(pkgJson.devDependencies || {}),
    unused: depcheckResult.unused,
    unusedDev: depcheckResult.unusedDev,
    missing: depcheckResult.missing,
    outdated,
  };

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: "You're a dependency audit expert. Analyze the project dependencies and give actionable advice. Be concise, use bullet points. Mention specific packages by name. Flag any security concerns you know about."
      },
      {
        role: "user",
        content: `Audit these dependencies:\n${JSON.stringify(context, null, 2)}`
      }
    ],
    temperature: 0.3,
  });

  return response.choices[0]?.message?.content?.trim() || "";
}

export async function removeDeps(dir: string, deps: string[]): Promise<void> {
  if (deps.length === 0) return;
  execSync(`npm uninstall ${deps.join(" ")}`, { cwd: dir, stdio: "inherit" });
}
