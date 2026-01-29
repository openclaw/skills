import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";
import { createPatch } from "diff";
import chalk from "chalk";

export interface RefactorOptions {
  filePath: string;
  apply?: boolean;
  focus?: string;
}

export interface RefactorResult {
  original: string;
  refactored: string;
  explanation: string;
  diff: string;
}

function colorDiff(patch: string): string {
  return patch
    .split("\n")
    .map((line) => {
      if (line.startsWith("+") && !line.startsWith("+++")) {
        return chalk.green(line);
      }
      if (line.startsWith("-") && !line.startsWith("---")) {
        return chalk.red(line);
      }
      if (line.startsWith("@@")) {
        return chalk.cyan(line);
      }
      return line;
    })
    .join("\n");
}

export async function analyzeAndRefactor(
  options: RefactorOptions
): Promise<RefactorResult> {
  const resolved = path.resolve(process.cwd(), options.filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`File not found: ${resolved}`);
  }

  const original = fs.readFileSync(resolved, "utf-8");
  const ext = path.extname(resolved);

  const openai = new OpenAI();

  const focusPrompt = options.focus
    ? `Focus specifically on: ${options.focus}.`
    : "";

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a senior code reviewer. Analyze the given ${ext} file and suggest refactoring improvements. ${focusPrompt}

Return your response in this exact JSON format:
{
  "explanation": "Brief summary of what you changed and why",
  "refactored": "The complete refactored file content"
}

Focus on: readability, performance, modern patterns, reducing duplication, better naming. Don't change functionality. Output valid JSON only.`,
      },
      {
        role: "user",
        content: original,
      },
    ],
    temperature: 0.3,
    response_format: { type: "json_object" },
  });

  const content = response.choices[0]?.message?.content || "{}";
  let parsed: { explanation?: string; refactored?: string };

  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error("Failed to parse AI response. Try again.");
  }

  const refactored = parsed.refactored || original;
  const explanation = parsed.explanation || "No changes suggested.";
  const diff = createPatch(options.filePath, original, refactored);

  return { original, refactored, explanation, diff };
}

export function applyRefactor(filePath: string, content: string): void {
  const resolved = path.resolve(process.cwd(), filePath);
  fs.writeFileSync(resolved, content, "utf-8");
}

export { colorDiff };
