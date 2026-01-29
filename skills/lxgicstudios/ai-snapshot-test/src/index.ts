import OpenAI from "openai";
import { readFileSync, writeFileSync } from "fs";
import { basename, dirname, join } from "path";

const openai = new OpenAI();

export async function generateSnapshotTest(filePath: string): Promise<{ testCode: string; testPath: string }> {
  const code = readFileSync(filePath, "utf-8");
  const ext = filePath.endsWith(".tsx") ? "tsx" : filePath.endsWith(".ts") ? "ts" : filePath.endsWith(".jsx") ? "jsx" : "js";
  const name = basename(filePath, `.${ext}`);
  const testPath = join(dirname(filePath), `${name}.snap.test.${ext}`);

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You generate Jest snapshot tests for React components. Rules:
- Use @testing-library/react with render
- Test all prop variations and states
- Use toMatchSnapshot() for each render
- Import from the relative source file
- Include tests for: default props, all prop combos, edge cases, conditional renders
Return ONLY the test file code, no explanation.` },
      { role: "user", content: code }
    ],
    temperature: 0.3,
  });

  return { testCode: response.choices[0].message.content?.trim() || "", testPath };
}

export function writeTestFile(path: string, code: string): void {
  writeFileSync(path, code);
}
