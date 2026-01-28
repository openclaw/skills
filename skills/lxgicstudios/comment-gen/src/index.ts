import OpenAI from "openai";
import { readFileSync, writeFileSync } from "fs";

const openai = new OpenAI();

export async function addComments(filePath: string, style: string): Promise<string> {
  const code = readFileSync(filePath, "utf-8");

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You add inline comments to code. Style: ${style}.
Rules:
- Only comment complex, non-obvious logic
- Don't comment simple assignments or obvious operations
- Use the language's comment syntax
- Keep comments concise (1 line each)
- Explain WHY, not WHAT
- Don't modify the code itself, only add comments
Return the full file with comments added.` },
      { role: "user", content: code }
    ],
    temperature: 0.3,
  });

  return response.choices[0].message.content?.trim() || code;
}
