import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";

const openai = new OpenAI();

export async function generateSeedData(schemaPath: string, count: number = 10): Promise<string> {
  const absPath = path.resolve(schemaPath);
  const schema = fs.readFileSync(absPath, "utf-8");

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You generate realistic database seed data from schema definitions.
Rules:
- Generate ${count} records per model/table
- Use realistic names, emails, dates, addresses (not "test1", "foo", etc.)
- Respect foreign key relationships and constraints
- Include proper data types (dates as ISO strings, UUIDs where needed)
- Generate a complete seed script that can be run directly
- Detect the ORM (Prisma, Drizzle, TypeORM, Knex, raw SQL) from the schema format
- Return ONLY the seed script code, no explanations`
      },
      { role: "user", content: schema }
    ],
    temperature: 0.5,
  });

  const result = response.choices[0].message.content?.trim() || "";
  return result.replace(/^```[\w]*\n?/, "").replace(/\n?```$/, "");
}
