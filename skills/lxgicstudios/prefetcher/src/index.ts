import OpenAI from "openai";
import * as fs from "fs";
import { glob } from "glob";

const openai = new OpenAI();

export async function scanPages(dir: string): Promise<string[]> {
  const files = await glob("**/*.{js,ts,jsx,tsx,vue,svelte}", {
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

export async function suggestPrefetch(codeChunks: string[]): Promise<string> {
  const combined = codeChunks.join("\n\n").substring(0, 60000);
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are a frontend performance expert. Analyze the page/route code and suggest what routes, data, and assets should be prefetched for better UX. Consider: link prefetch, DNS prefetch, preconnect, route preloading, data prefetching patterns. Provide implementation code. Be concise." },
      { role: "user", content: combined }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "No prefetch suggestions.";
}
