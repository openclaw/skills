import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function roastCode(filePath: string, intensity: string = "medium"): Promise<string> {
  const content = fs.readFileSync(filePath, "utf-8");
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You're a senior dev who roasts code with humor. Intensity: ${intensity} (mild = gentle teasing, medium = solid burns, savage = no mercy). Rules:
- Be genuinely funny, not mean-spirited
- Every roast must include an actual improvement suggestion
- Rate the code 1-10 at the end
- Use emojis sparingly
- Keep it real. If the code is actually good, say so (but still find something to roast)`
      },
      { role: "user", content: `File: ${path.basename(filePath)}\n\n${content}` }
    ],
    temperature: 0.8,
  });
  return response.choices[0].message.content || "";
}
