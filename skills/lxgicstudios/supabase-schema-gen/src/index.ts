import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generate(filePath: string): Promise<string> {
  let content: string;
  const resolved = path.resolve(filePath);

  if (fs.statSync(resolved).isDirectory()) {
    const files = fs.readdirSync(resolved).filter(f => /\.(ts|js|prisma)$/.test(f));
    content = files.map(f => {
      const fp = path.join(resolved, f);
      return `// File: ${f}\n${fs.readFileSync(fp, "utf-8")}`;
    }).join("\n\n");
  } else {
    content = fs.readFileSync(resolved, "utf-8");
  }

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a Supabase security expert. Read the Prisma schema provided and generate Row Level Security (RLS) policies as SQL. Include: enable RLS on all tables, policies for authenticated users (select own data, insert own data, update own data, delete own data), service role bypass, and any join-table policies. Output valid PostgreSQL/Supabase SQL.` },
      { role: "user", content: `File: ${path.basename(filePath)}\n\n${content}` }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "";
}
