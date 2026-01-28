import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const userContent = `Generate an ETL script for this transformation: ${input}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a data engineering expert. Generate a complete, working ETL script for the requested transformation. Use Node.js by default. Include error handling, logging, and batch processing where appropriate. Add comments explaining the approach. Output production-ready code.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
