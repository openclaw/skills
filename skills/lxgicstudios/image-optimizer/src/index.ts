import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";
import { glob } from "glob";

const openai = new OpenAI();

export interface ImageInfo {
  file: string;
  size: number;
  extension: string;
}

export async function scanImages(dir: string): Promise<ImageInfo[]> {
  const files = await glob("**/*.{jpg,jpeg,png,gif,webp,svg,bmp,tiff,ico}", {
    cwd: dir, absolute: true, ignore: ["**/node_modules/**", "**/dist/**", "**/.git/**"]
  });
  const images: ImageInfo[] = [];
  for (const f of files) {
    try {
      const stats = fs.statSync(f);
      images.push({ file: f, size: stats.size, extension: path.extname(f).toLowerCase() });
    } catch {}
  }
  return images.sort((a, b) => b.size - a.size);
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

export async function getOptimizationAdvice(images: ImageInfo[]): Promise<string> {
  const summary = images.map(i => `${i.file} - ${formatSize(i.size)} (${i.extension})`).join("\n");
  const totalSize = images.reduce((s, i) => s + i.size, 0);
  const context = `Total images: ${images.length}\nTotal size: ${formatSize(totalSize)}\n\nFiles (sorted by size):\n${summary}`;
  
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are an image optimization expert. Analyze the image inventory and suggest optimizations: format conversion (WebP/AVIF), compression, resizing, lazy loading, responsive images, SVG optimization, sprite sheets. Prioritize by size savings. Include specific commands (sharp, imagemin, squoosh). Be concise and actionable." },
      { role: "user", content: context.substring(0, 30000) }
    ],
    temperature: 0.3,
  });
  return response.choices[0].message.content || "No optimization suggestions.";
}
