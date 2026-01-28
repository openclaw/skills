import * as fs from "fs-extra";
import * as path from "path";
import { glob } from "glob";
import OpenAI from "openai";
import ora from "ora";

export interface DocsOptions {
  paths: string[];
  style: string;
  write: boolean;
}

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

export async function addDocs(opts: DocsOptions): Promise<void> {
  const spinner = ora("Finding source files...").start();

  let resolvedFiles: string[] = [];
  for (const p of opts.paths) {
    const stat = await fs.stat(p).catch(() => null);
    if (stat?.isDirectory()) {
      const matches = await glob(path.join(p, "**/*.{ts,tsx,js,jsx}"));
      resolvedFiles.push(...matches);
    } else {
      const matches = await glob(p);
      resolvedFiles.push(...matches);
    }
  }

  // Filter out node_modules and dist
  resolvedFiles = resolvedFiles.filter(
    (f) => !f.includes("node_modules") && !f.includes("/dist/")
  );

  if (resolvedFiles.length === 0) {
    spinner.fail("No source files found.");
    process.exit(1);
  }

  spinner.succeed(`Found ${resolvedFiles.length} file(s)`);

  const openai = getOpenAI();

  for (const file of resolvedFiles) {
    const fileSpinner = ora(`Documenting ${file}...`).start();
    const content = await fs.readFile(file, "utf-8");

    if (content.length > 20000) {
      fileSpinner.warn(`${file} is too large, skipping.`);
      continue;
    }

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            `You're adding ${opts.style} documentation comments to source code. ` +
            "Add doc comments to all exported functions, classes, interfaces, and types. " +
            "Don't change any code logic. Keep existing comments. " +
            "Output the COMPLETE file with comments added. Nothing else.",
        },
        {
          role: "user",
          content: `Add ${opts.style} comments to this file:\n\n${content}`,
        },
      ],
    });

    const documented = response.choices[0]?.message?.content || "";

    // Strip markdown code fences if present
    const cleaned = documented
      .replace(/^```(?:typescript|javascript|tsx|jsx)?\n/, "")
      .replace(/\n```$/, "");

    if (opts.write) {
      await fs.writeFile(file, cleaned);
      fileSpinner.succeed(`Updated ${file}`);
    } else {
      fileSpinner.succeed(`${file}`);
      console.log("\n" + cleaned + "\n");
    }
  }
}
