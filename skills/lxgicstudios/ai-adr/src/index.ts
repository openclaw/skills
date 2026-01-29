import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  let context = "";
  try { const pkg = JSON.parse(fs.readFileSync(path.join(process.cwd(), "package.json"), "utf-8")); context = `Project: ${pkg.name}, deps: ${JSON.stringify(Object.keys({...pkg.dependencies}))}`; } catch {}
  const userContent = `Generate an ADR for this decision: ${input}\n\nProject context: ${context}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a software architect. Generate a well-structured Architecture Decision Record (ADR) in markdown format. Include: Title, Date, Status (Proposed), Context, Decision, Consequences (positive and negative), and Alternatives Considered. Be thorough but concise.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
