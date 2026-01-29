import OpenAI from "openai";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export function runLighthouse(url: string): string {
  const tmpFile = path.join("/tmp", `lighthouse-${Date.now()}.json`);
  try {
    execSync(`npx lighthouse "${url}" --output=json --output-path="${tmpFile}" --chrome-flags="--headless --no-sandbox" --quiet`, {
      timeout: 120000, stdio: "pipe"
    });
    const result = fs.readFileSync(tmpFile, "utf-8");
    fs.unlinkSync(tmpFile);
    return result;
  } catch (err: any) {
    if (fs.existsSync(tmpFile)) {
      const result = fs.readFileSync(tmpFile, "utf-8");
      fs.unlinkSync(tmpFile);
      return result;
    }
    throw new Error(`Lighthouse failed: ${err.message}`);
  }
}

export function summarizeReport(report: string): string {
  try {
    const data = JSON.parse(report);
    const cats = data.categories || {};
    const summary: string[] = [];
    for (const [key, val] of Object.entries(cats) as any) {
      summary.push(`${val.title}: ${Math.round((val.score || 0) * 100)}/100`);
    }
    const audits = data.audits || {};
    const failed: string[] = [];
    for (const [key, val] of Object.entries(audits) as any) {
      if (val.score !== null && val.score < 0.5) {
        failed.push(`- ${val.title}: ${val.displayValue || "needs improvement"}`);
      }
    }
    return `Scores:\n${summary.join("\n")}\n\nFailing Audits:\n${failed.slice(0, 20).join("\n")}`;
  } catch {
    return report.substring(0, 5000);
  }
}

export async function getAIFixes(summary: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are a web performance expert. Given Lighthouse audit results, provide specific, actionable fixes prioritized by impact. Include code snippets where helpful. Focus on the biggest wins first. Be concise." },
      { role: "user", content: summary }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "No suggestions.";
}
