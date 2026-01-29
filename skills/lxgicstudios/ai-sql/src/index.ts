import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function generateSQL(query: string, options: { dialect?: string; schema?: string }): Promise<string> {
  const dialect = options.dialect || "PostgreSQL";

  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a database expert. Convert natural language to ${dialect} SQL queries. Use best practices: proper indexing hints, parameterized placeholders where appropriate, and clear aliases.${options.schema ? ` The database schema is: ${options.schema}` : ""} Return ONLY the SQL query, no explanation.`,
      },
      {
        role: "user",
        content: query,
      },
    ],
    temperature: 0.2,
  });
  return res.choices[0].message.content || "";
}
