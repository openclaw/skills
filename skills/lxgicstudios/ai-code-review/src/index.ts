import simpleGit from "simple-git";
import OpenAI from "openai";
import ora from "ora";
import chalk from "chalk";

function getOpenAI(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error(
      "Missing OPENAI_API_KEY environment variable.\n" +
      "Get one at https://platform.openai.com/api-keys then:\n" +
      "  export OPENAI_API_KEY=sk-..."
    );
    process.exit(1);
  }
  return new OpenAI({ apiKey });
}

export async function reviewStagedChanges(): Promise<void> {
  const git = simpleGit();
  const spinner = ora("Reading staged changes...").start();

  let diff: string;
  try {
    diff = await git.diff(["--cached"]);
  } catch {
    spinner.fail("Couldn't read staged changes. Are you in a git repo?");
    process.exit(1);
  }

  if (!diff.trim()) {
    spinner.fail("No staged changes found. Stage some files with git add first.");
    process.exit(1);
  }

  const truncatedDiff = diff.length > 15000 ? diff.substring(0, 15000) + "\n...(truncated)" : diff;

  spinner.text = "Reviewing your code...";

  const openai = getOpenAI();
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You're a senior developer doing a code review. Be direct and helpful. " +
          "For each issue, use this format:\n" +
          "[SEVERITY] file:line - description\n\n" +
          "Severities: CRITICAL, WARNING, SUGGESTION, GOOD\n" +
          "CRITICAL = bugs, security issues\n" +
          "WARNING = code smells, potential problems\n" +
          "SUGGESTION = style, readability improvements\n" +
          "GOOD = things done well (include a few)\n\n" +
          "End with a brief summary. Be specific, reference actual code.",
      },
      {
        role: "user",
        content: `Review this diff:\n\n${truncatedDiff}`,
      },
    ],
  });

  spinner.succeed("Review complete!");

  const review = response.choices[0]?.message?.content || "No output.";

  // Colorize output
  const colored = review
    .replace(/\[CRITICAL\]/g, chalk.red.bold("[CRITICAL]"))
    .replace(/\[WARNING\]/g, chalk.yellow.bold("[WARNING]"))
    .replace(/\[SUGGESTION\]/g, chalk.cyan("[SUGGESTION]"))
    .replace(/\[GOOD\]/g, chalk.green("[GOOD]"));

  console.log("\n" + colored);
}
