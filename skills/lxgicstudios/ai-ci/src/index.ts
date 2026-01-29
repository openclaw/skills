import OpenAI from "openai";
import { glob } from "glob";
import * as fs from "fs";
import * as path from "path";

const CONFIG_FILES = [
  "package.json", "tsconfig.json", "next.config.js", "next.config.mjs",
  "vite.config.ts", "nuxt.config.ts", "Cargo.toml", "go.mod",
  "pyproject.toml", "requirements.txt", "Gemfile", "build.gradle", "pom.xml",
  "jest.config.js", "jest.config.ts", "vitest.config.ts", ".eslintrc.js",
  ".eslintrc.json", "prettier.config.js", "Makefile",
  "docker-compose.yml", "Dockerfile", "vercel.json", "netlify.toml",
  "fly.toml", "railway.json",
];

export async function scanProject(dir: string): Promise<{ files: string[]; contents: Record<string, string> }> {
  const found: string[] = [];
  const contents: Record<string, string> = {};

  for (const f of CONFIG_FILES) {
    const full = path.join(dir, f);
    if (fs.existsSync(full)) {
      found.push(f);
      const stat = fs.statSync(full);
      if (stat.size < 5000) {
        contents[f] = fs.readFileSync(full, "utf-8");
      }
    }
  }

  return { files: found, contents };
}

export async function generateWorkflow(
  projectInfo: { files: string[]; contents: Record<string, string> },
  provider: string,
  deployTarget?: string
): Promise<string> {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("Missing OPENAI_API_KEY environment variable. Set it with: export OPENAI_API_KEY=sk-...");
  }

  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const deployInstruction = deployTarget
    ? `Include a deployment step for ${deployTarget}. Use the standard ${deployTarget} GitHub Action or deployment method.`
    : "Don't include deployment steps, just CI (lint, test, build).";

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a CI/CD expert. Generate a ${provider === "github" ? "GitHub Actions" : provider} workflow YAML file. Output ONLY the YAML contents. No markdown code fences. Include proper caching, matrix testing if appropriate, and best practices. ${deployInstruction}`
      },
      {
        role: "user",
        content: `Project files: ${projectInfo.files.join(", ")}\n\nKey file contents:\n${Object.entries(projectInfo.contents).map(([k, v]) => `--- ${k} ---\n${v}`).join("\n\n")}`
      }
    ],
    temperature: 0.3,
  });

  return response.choices[0]?.message?.content?.trim() || "";
}
