import OpenAI from "openai";
import { execSync } from "child_process";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function getAuditOutput(): Promise<string> {
  try {
    return execSync("npm audit --json 2>/dev/null", { encoding: "utf-8" });
  } catch (err: any) {
    return err.stdout || err.message;
  }
}

export async function analyzeAudit(auditJson: string): Promise<string> {
  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You are a security expert. Analyze npm audit JSON output and provide: 1) A summary of vulnerabilities found (critical, high, moderate, low counts), 2) For each vulnerability, explain what it is and the risk, 3) Specific fix commands (npm audit fix, manual overrides, or package replacements). Be concise and actionable.",
      },
      {
        role: "user",
        content: `Analyze this npm audit output and suggest fixes:\n\n${auditJson.slice(0, 8000)}`,
      },
    ],
    temperature: 0.3,
  });
  return res.choices[0].message.content || "No analysis generated.";
}
