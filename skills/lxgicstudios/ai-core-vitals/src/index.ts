import OpenAI from "openai";
import * as fs from "fs";
import { glob } from "glob";

const openai = new OpenAI();

export async function scanSourceFiles(dir: string): Promise<string[]> {
  const files = await glob("**/*.{js,ts,jsx,tsx,html,css,vue,svelte}", {
    cwd: dir, absolute: true, ignore: ["**/node_modules/**", "**/dist/**", "**/.git/**"]
  });
  const contents: string[] = [];
  for (const f of files) {
    try {
      const content = fs.readFileSync(f, "utf-8");
      if (content.length > 0 && content.length < 50000) {
        contents.push(`// File: ${f}\n${content}`);
      }
    } catch {}
  }
  return contents;
}

export async function fixCoreVitals(codeChunks: string[]): Promise<string> {
  const combined = codeChunks.join("\n\n").substring(0, 60000);
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are a Core Web Vitals expert. Analyze the code for issues affecting LCP (Largest Contentful Paint), FID/INP (First Input Delay/Interaction to Next Paint), and CLS (Cumulative Layout Shift). For each issue, explain the problem, its impact on the specific metric, and provide a concrete code fix. Prioritize by impact. Be concise." },
      { role: "user", content: combined }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "No Core Web Vitals issues found.";
}
