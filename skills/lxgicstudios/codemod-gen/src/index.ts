import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const userContent = `Generate a jscodeshift codemod for: ${input}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are an expert codemod generator. Given a description of a code transformation, generate a working jscodeshift codemod that performs the transformation. Include comments explaining each step. Output only the codemod code.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
