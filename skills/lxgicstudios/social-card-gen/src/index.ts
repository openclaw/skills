import OpenAI from "openai";
import * as fs from "fs";

const openai = new OpenAI();

export type Platform = "twitter" | "linkedin" | "reddit" | "all";

const PLATFORM_PROMPTS: Record<string, string> = {
  twitter: `Write a Twitter/X post (max 280 chars). Make it punchy, use 1-2 relevant hashtags. Hook people in the first line. No fluff.`,
  linkedin: `Write a LinkedIn post (max 1300 chars). Professional but not boring. Use line breaks for readability. Include a call to action. Start with a hook that makes people stop scrolling.`,
  reddit: `Write a Reddit post with a title and body. Be genuine, not promotional. Reddit hates marketing speak. Write like you're sharing something useful with the community. Include a brief title line starting with "Title:" then the body.`,
};

export async function generatePost(content: string, platform: Platform): Promise<Record<string, string>> {
  const platforms = platform === "all" ? ["twitter", "linkedin", "reddit"] : [platform];
  const results: Record<string, string> = {};

  for (const p of platforms) {
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: `You turn blog posts and documentation into social media posts. ${PLATFORM_PROMPTS[p]} Return ONLY the post text, nothing else.`
        },
        { role: "user", content: `Turn this into a ${p} post:\n\n${content}` }
      ],
      temperature: 0.7,
    });

    results[p] = response.choices[0].message.content?.trim() || "";
  }

  return results;
}

export async function generateFromFile(filePath: string, platform: Platform): Promise<Record<string, string>> {
  const content = fs.readFileSync(filePath, "utf-8");
  return generatePost(content, platform);
}
