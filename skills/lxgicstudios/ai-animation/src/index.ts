import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function generateAnimation(description: string, options: { format?: string }): Promise<string> {
  const format = options.format || "both";
  let outputInstructions = "";
  if (format === "css") outputInstructions = "Generate CSS @keyframes animation only.";
  else if (format === "framer") outputInstructions = "Generate Framer Motion animation config only (motion component props).";
  else outputInstructions = "Generate both CSS @keyframes and Framer Motion equivalent.";

  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a frontend animation expert. ${outputInstructions} Include proper easing, timing, and clean code. Return ONLY the code, no explanation.`,
      },
      {
        role: "user",
        content: `Create animation: ${description}`,
      },
    ],
    temperature: 0.4,
  });
  return res.choices[0].message.content || "";
}
