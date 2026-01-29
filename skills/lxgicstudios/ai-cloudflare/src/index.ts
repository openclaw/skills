import OpenAI from "openai";

const openai = new OpenAI();

export async function generate(description: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a Cloudflare Workers expert. Generate complete Workers setup from the description. Include: wrangler.toml config, worker TypeScript code, KV/D1/R2 bindings if needed, routing, environment variables, rate limiting, caching strategies, error handling, and deployment instructions. Follow Cloudflare best practices.` },
      { role: "user", content: description }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "";
}
