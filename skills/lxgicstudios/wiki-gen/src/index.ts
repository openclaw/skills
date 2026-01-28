import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const files = fs.readdirSync(input, { recursive: true }) as string[];
  const codeFiles = files.filter((f: string) => /\.(ts|tsx|js|jsx)$/.test(f)).slice(0, 25);
  const contents = codeFiles.map((f: string) => {
    try { return `--- ${f} ---\n` + fs.readFileSync(path.join(input, f), "utf-8").slice(0, 2000); } catch { return ""; }
  }).join("\n\n");
  const userContent = `Generate wiki documentation for this codebase:\n\n${contents}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a technical documentation expert. Analyze the codebase and generate comprehensive wiki pages in markdown. Include: Overview, Architecture, Module docs, API reference, and Getting Started. Create interlinked pages with a table of contents. Be thorough but readable.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
