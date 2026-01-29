import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function convertCssToTailwind(filePath: string): Promise<string> {
  const absPath = path.resolve(filePath);
  const content = fs.readFileSync(absPath, "utf-8");

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You convert CSS to Tailwind CSS utility classes.
Rules:
- Map each CSS property to its Tailwind equivalent
- Group related utilities logically
- Use Tailwind v3 syntax
- For complex selectors, provide the class list with a comment showing the original selector
- Output format: a mapping of original CSS selectors to their Tailwind class strings
- Return as a clean, readable reference document
- If a property has no direct Tailwind equivalent, note it with a comment`
      },
      { role: "user", content: content }
    ],
    temperature: 0.2,
  });

  return response.choices[0].message.content?.trim() || "";
}
