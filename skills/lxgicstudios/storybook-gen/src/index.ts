import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const content = fs.readFileSync(input, "utf-8");
  const userContent = `Generate Storybook stories for this component:\n\nFile: ${path.basename(input)}\n\n${content}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a Storybook expert. Analyze the React component and generate comprehensive Storybook stories using CSF3 format. Include: default story, all meaningful prop variations, edge cases, and interactive examples with args. Use TypeScript. Add proper decorators if needed.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
