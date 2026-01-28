import OpenAI from "openai";
import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync } from "fs";
import { join } from "path";
import { execSync } from "child_process";

const openai = new OpenAI();

export async function analyzeProject(): Promise<string> {
  const cwd = process.cwd();
  let pkgContent = "{}";
  try { pkgContent = readFileSync(join(cwd, "package.json"), "utf-8"); } catch {}
  return pkgContent;
}

export async function generateHooks(pkgContent: string): Promise<{ preCommit: string; prePush: string; commitMsg: string }> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You generate git hook scripts based on a project's package.json. Return JSON:
{ "preCommit": "#!/bin/sh\\nscript...", "prePush": "#!/bin/sh\\nscript...", "commitMsg": "#!/bin/sh\\nscript..." }
Pre-commit: lint staged files, type-check if typescript.
Pre-push: run tests.
Commit-msg: validate conventional commit format.
Use the project's actual scripts (lint, test, typecheck) from package.json.
Return ONLY valid JSON.` },
      { role: "user", content: pkgContent }
    ],
    temperature: 0.3,
  });

  return JSON.parse(response.choices[0].message.content || "{}");
}

export function installHooks(hooks: { preCommit: string; prePush: string; commitMsg: string }): void {
  const hooksDir = join(process.cwd(), ".husky");
  mkdirSync(hooksDir, { recursive: true });

  const write = (name: string, content: string) => {
    const path = join(hooksDir, name);
    writeFileSync(path, content);
    chmodSync(path, "755");
  };

  write("pre-commit", hooks.preCommit);
  write("pre-push", hooks.prePush);
  write("commit-msg", hooks.commitMsg);

  try {
    execSync("git config core.hooksPath .husky", { stdio: "pipe" });
  } catch {}
}
