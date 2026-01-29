import OpenAI from "openai";
import { readFileSync, writeFileSync, readdirSync, statSync } from "fs";
import { join, extname } from "path";

const openai = new OpenAI();

export function collectRouteFiles(dir: string): string[] {
  const files: string[] = [];
  const entries = readdirSync(dir);
  for (const entry of entries) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      files.push(...collectRouteFiles(full));
    } else if ([".ts", ".js", ".tsx", ".jsx"].includes(extname(full))) {
      files.push(full);
    }
  }
  return files;
}

export async function generateApiDocs(files: string[], format: string): Promise<string> {
  const code = files.map(f => `// ${f}\n${readFileSync(f, "utf-8")}`).join("\n\n");

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You generate API documentation from route/endpoint code. Output format: ${format}.
For markdown: include method, path, description, request/response examples, parameters, error codes.
For openapi: return valid OpenAPI 3.0 YAML spec.
Be thorough and accurate based on the actual code.` },
      { role: "user", content: code.slice(0, 12000) }
    ],
    temperature: 0.3,
  });

  return response.choices[0].message.content?.trim() || "";
}

export function writeDocs(path: string, content: string): void {
  writeFileSync(path, content);
}
