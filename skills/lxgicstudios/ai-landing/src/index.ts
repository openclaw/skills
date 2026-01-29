import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generateLanding(dir: string): Promise<string> {
  let context = "";
  const pkgPath = path.join(dir, "package.json");
  if (fs.existsSync(pkgPath)) {
    context = fs.readFileSync(pkgPath, "utf-8");
  }
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You generate modern, responsive HTML landing pages. Include: hero section with headline and CTA, features grid, installation/usage section, footer. Use inline CSS with a modern dark theme, smooth gradients, and clean typography. Make it a single self-contained HTML file. No external dependencies.` },
      { role: "user", content: `Generate a landing page for this project:\n\n${context || "A modern developer tool"}` }
    ],
    temperature: 0.6,
  });
  return response.choices[0].message.content || "";
}
