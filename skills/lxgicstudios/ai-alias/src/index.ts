import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  const histFile = process.env.HISTFILE || path.join(process.env.HOME || "~", ".zsh_history");
  let history = "";
  try { history = fs.readFileSync(histFile, "utf-8").split("\n").slice(-500).join("\n"); } catch { history = "No history file found. Generate common useful aliases for developers."; }
  const userContent = `Analyze this shell history and suggest aliases:\n\n${history}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a shell productivity expert. Analyze the command history and suggest useful shell aliases. Output them in a format ready to paste into .bashrc or .zshrc. Group by category (git, docker, npm, etc). Only suggest aliases for commands used frequently or that are long to type.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
