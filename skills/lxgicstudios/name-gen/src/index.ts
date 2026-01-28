import OpenAI from "openai";
import simpleGit from "simple-git";

const openai = new OpenAI();
const git = simpleGit();

export async function getStashDiff(): Promise<string> {
  const diff = await git.diff(["--cached"]);
  const unstaged = await git.diff();
  return (diff + "\n" + unstaged).slice(0, 4000);
}

export async function generateStashName(diff: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You generate short, descriptive git stash names from diffs. Return ONLY the stash message, no quotes. Keep it under 60 chars. Be specific about what changed." },
      { role: "user", content: diff }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content?.trim() || "wip: misc changes";
}

export async function stashWithName(): Promise<string> {
  const diff = await getStashDiff();
  if (!diff.trim()) throw new Error("No changes to stash");
  const name = await generateStashName(diff);
  await git.stash(["push", "-m", name]);
  return name;
}
