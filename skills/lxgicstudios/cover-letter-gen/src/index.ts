import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(input: string): Promise<string> {
  let resume = "";
  try { resume = fs.readFileSync(path.join(process.cwd(), "resume.md"), "utf-8"); } catch { try { resume = fs.readFileSync(path.join(process.cwd(), "resume.txt"), "utf-8"); } catch {} }
  const userContent = `Write a cover letter for: ${input}\n\n${resume ? "Resume context:\n" + resume : "No resume found. Write a general but compelling letter."}`;
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a career coach who writes compelling cover letters. Generate a professional but personable cover letter. Avoid corporate buzzwords. Be specific about why the role is interesting and what value the candidate brings. Keep it under 400 words. Sound human, not robotic.` },
      { role: "user", content: userContent }
    ],
    temperature: 0.7,
  });
  return response.choices[0].message.content || "";
}
