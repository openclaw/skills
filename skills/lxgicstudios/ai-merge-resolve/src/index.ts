import OpenAI from "openai";
import * as fs from "fs";

const openai = new OpenAI();

export async function resolveConflicts(content: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a merge conflict resolver. You receive file content with git merge conflict markers (<<<<<<< HEAD, =======, >>>>>>> branch). Analyze both sides and produce the best merged result. Return ONLY the resolved file content with no conflict markers. No explanations.`
      },
      { role: "user", content }
    ],
    temperature: 0.2,
  });
  return response.choices[0].message.content?.trim() || content;
}

export async function resolveFile(filePath: string): Promise<string> {
  const content = fs.readFileSync(filePath, "utf-8");
  if (!content.includes("<<<<<<<")) {
    throw new Error("No merge conflict markers found in file");
  }
  return resolveConflicts(content);
}
