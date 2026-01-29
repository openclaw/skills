import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  let context = "";
  try { const pkg = JSON.parse(fs.readFileSync(path.join(process.cwd(), "package.json"), "utf-8")); context = `Current package.json deps: ${JSON.stringify(Object.keys({...pkg.dependencies, ...pkg.devDependencies}))}`; } catch {}
  const userContent = `Generate npm scripts for these tasks: ${input}\n\n${context}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a package.json scripts expert. Generate practical npm scripts for the requested tasks. Use common tools (eslint, jest, tsc, esbuild, etc). Output valid JSON that can be merged into the scripts field of package.json. Include pre/post hooks where useful.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
