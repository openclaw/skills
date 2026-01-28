import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function generateWorkflow(description: string): Promise<string> {
  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: "You are a DevOps expert. Generate a complete GitHub Actions workflow YAML file based on the description. Use best practices: proper triggers, caching, environment variables, and job dependencies. Return ONLY the YAML content, no explanation.",
      },
      {
        role: "user",
        content: `Create a GitHub Actions workflow: ${description}`,
      },
    ],
    temperature: 0.3,
  });
  return res.choices[0].message.content || "";
}
