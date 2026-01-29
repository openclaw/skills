import simpleGit from "simple-git";
import OpenAI from "openai";
import ora from "ora";

export interface ChangelogOptions {
  from: string;
  to: string;
  output?: string;
}

function getOpenAI(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error(
      "Missing OPENAI_API_KEY environment variable.\n" +
      "Grab one from https://platform.openai.com/api-keys and set it:\n" +
      "  export OPENAI_API_KEY=sk-..."
    );
    process.exit(1);
  }
  return new OpenAI({ apiKey });
}

export async function generateChangelog(opts: ChangelogOptions): Promise<string> {
  const git = simpleGit();
  const spinner = ora("Reading git log...").start();

  let log: string;
  try {
    log = await git.raw(["log", `${opts.from}..${opts.to}`, "--pretty=format:%h %s (%an)", "--no-merges"]);
  } catch (err: any) {
    spinner.fail("Couldn't read git log. Are you in a git repo?");
    throw err;
  }

  if (!log.trim()) {
    spinner.fail(`No commits found between ${opts.from} and ${opts.to}`);
    process.exit(1);
  }

  spinner.text = "Generating changelog with OpenAI...";

  const openai = getOpenAI();
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You're a developer writing a clean CHANGELOG.md entry. " +
          "Group commits into categories like Added, Changed, Fixed, Removed. " +
          "Use markdown format. Be concise. Skip boring merge commits. " +
          "Write like a human, not a robot.",
      },
      {
        role: "user",
        content:
          `Generate a changelog entry for ${opts.from} to ${opts.to}.\n\nCommits:\n${log}`,
      },
    ],
  });

  spinner.succeed("Changelog generated!");
  return response.choices[0]?.message?.content || "No output from OpenAI.";
}
