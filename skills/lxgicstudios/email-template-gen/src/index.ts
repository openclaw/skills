import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function generateEmailTemplate(description: string, options: { format?: string }): Promise<string> {
  const format = options.format || "html";
  let formatInstr = "responsive HTML email with inline CSS";
  if (format === "react") formatInstr = "React Email component (using @react-email/components)";
  if (format === "mjml") formatInstr = "MJML template";

  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are an email design expert. Generate a ${formatInstr} that works across all major email clients (Gmail, Outlook, Apple Mail). Use table-based layout for HTML. Include proper spacing, typography, and a clean professional design. Return ONLY the code, no explanation.`,
      },
      {
        role: "user",
        content: `Create email template: ${description}`,
      },
    ],
    temperature: 0.4,
  });
  return res.choices[0].message.content || "";
}
