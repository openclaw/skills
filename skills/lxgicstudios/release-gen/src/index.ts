import OpenAI from "openai";
import simpleGit from "simple-git";
import { readFileSync } from "fs";
import { join } from "path";

const openai = new OpenAI();
const git = simpleGit();

export async function getCommitsSinceLastTag(): Promise<string> {
  try {
    const tags = await git.tags();
    const latest = tags.latest;
    if (latest) {
      const log = await git.log({ from: latest, to: "HEAD" });
      return log.all.map(c => c.message).join("\n");
    }
  } catch {}
  const log = await git.log({ maxCount: 20 });
  return log.all.map(c => c.message).join("\n");
}

export async function getCurrentVersion(): Promise<string> {
  try {
    const pkg = JSON.parse(readFileSync(join(process.cwd(), "package.json"), "utf-8"));
    return pkg.version || "0.0.0";
  } catch { return "0.0.0"; }
}

export interface ReleaseInfo {
  version: string;
  bump: string;
  notes: string;
}

export async function generateRelease(commits: string, currentVersion: string): Promise<ReleaseInfo> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You analyze git commits and determine the semantic version bump. Current version: ${currentVersion}.
Return JSON with: { "bump": "patch|minor|major", "version": "x.y.z", "notes": "markdown release notes" }
Follow semver: breaking changes = major, new features = minor, fixes = patch.
Return ONLY valid JSON.` },
      { role: "user", content: commits }
    ],
    temperature: 0.3,
  });
  return JSON.parse(response.choices[0].message.content || "{}");
}

export async function createTag(version: string, notes: string): Promise<void> {
  await git.addAnnotatedTag(`v${version}`, notes);
}
