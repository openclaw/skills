import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const cwd = input;
  let context = "";
  try { context += "package.json:\n" + fs.readFileSync(path.join(cwd, "package.json"), "utf-8") + "\n\n"; } catch {}
  try { context += "README.md:\n" + fs.readFileSync(path.join(cwd, "README.md"), "utf-8").slice(0, 3000) + "\n\n"; } catch {}
  try { const files = fs.readdirSync(cwd, { recursive: true }) as string[]; context += "File tree:\n" + files.slice(0, 100).join("\n"); } catch {}
  const userContent = `Generate onboarding docs for this project:\n\n${context}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a developer onboarding expert. Analyze the project structure and generate a comprehensive onboarding guide for new developers. Include: project overview, setup instructions, architecture overview, key files, development workflow, testing approach, and common gotchas. Make it practical and friendly.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
