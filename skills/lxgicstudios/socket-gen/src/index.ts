import OpenAI from "openai";

const openai = new OpenAI();

export async function generate(description: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You are a WebSocket expert. Generate complete Socket.io server and client setup from the description. Include: server setup with namespaces, event handlers, rooms, authentication middleware, TypeScript types for events, client-side connection code, error handling, reconnection logic, and rate limiting. Follow Socket.io best practices.` },
      { role: "user", content: description }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "";
}
