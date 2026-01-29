import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function suggestIndexes(dirPath: string): Promise<string> {
  const absDir = path.resolve(dirPath);
  const stat = fs.statSync(absDir);
  let queryCode = "";

  if (stat.isDirectory()) {
    const files = fs.readdirSync(absDir).filter(f => /\.(ts|js|sql)$/.test(f));
    for (const file of files) {
      const content = fs.readFileSync(path.join(absDir, file), "utf-8");
      queryCode += `\n// === ${file} ===\n${content}\n`;
    }
  } else {
    queryCode = fs.readFileSync(absDir, "utf-8");
  }

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a database performance expert. Analyze query patterns and suggest optimal indexes.
For each suggestion include:
- The CREATE INDEX statement
- Which queries it optimizes
- Expected performance impact
- Whether it's a single-column, composite, or partial index
- Any trade-offs (write overhead, storage)
Be specific and practical. Return a well-formatted analysis.`
      },
      { role: "user", content: queryCode }
    ],
    temperature: 0.3,
  });

  return response.choices[0].message.content?.trim() || "";
}
