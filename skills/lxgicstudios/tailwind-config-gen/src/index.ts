import OpenAI from "openai";

const openai = new OpenAI();

export async function generateTailwind(colors: string[]): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: `You generate tailwind.config.js files. Given brand colors, create a complete design system with: color palette (shades 50-950 for each brand color), custom fonts, spacing scale, border radius, box shadows, and screen breakpoints. Output valid JavaScript module.exports config.` },
      { role: "user", content: `Generate a tailwind config with these brand colors: ${colors.join(", ")}` }
    ],
    temperature: 0.4,
  });
  return response.choices[0].message.content || "";
}
