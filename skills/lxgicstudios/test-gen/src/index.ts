import * as fs from "fs";
import * as path from "path";
import { glob } from "glob";
import OpenAI from "openai";
import ora from "ora";

export interface TestGenOptions {
  files: string[];
  framework: string;
  output?: string;
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

export async function generateTests(opts: TestGenOptions): Promise<string> {
  const spinner = ora("Reading source files...").start();

  // Resolve glob patterns
  let resolvedFiles: string[] = [];
  for (const pattern of opts.files) {
    const matches = await glob(pattern);
    resolvedFiles.push(...matches);
  }

  if (resolvedFiles.length === 0) {
    spinner.fail("No files found matching the given pattern.");
    process.exit(1);
  }

  // Read file contents
  const sources: string[] = [];
  for (const file of resolvedFiles) {
    const content = fs.readFileSync(file, "utf-8");
    sources.push(`// File: ${file}\n${content}`);
  }

  const allSource = sources.join("\n\n");
  const truncated = allSource.length > 15000 ? allSource.substring(0, 15000) + "\n...(truncated)" : allSource;

  spinner.text = `Generating ${opts.framework} tests...`;

  const openai = getOpenAI();
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          `You're a developer writing unit tests using ${opts.framework}. ` +
          "Write thorough tests that cover happy paths, edge cases, and error cases. " +
          "Use descriptive test names. Include imports. " +
          "Output ONLY the test file content, no explanation.",
      },
      {
        role: "user",
        content: `Generate ${opts.framework} unit tests for:\n\n${truncated}`,
      },
    ],
  });

  spinner.succeed("Tests generated!");
  return response.choices[0]?.message?.content || "No output from OpenAI.";
}
