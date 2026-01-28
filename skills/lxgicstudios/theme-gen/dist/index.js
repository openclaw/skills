"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateTheme = generateTheme;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default();
async function generateTheme(colors, format = "css") {
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You are a design system expert. Generate a complete theme/design system from the given brand colors.
Include:
- Full color palette (primary, secondary, accent, neutral, success, warning, error shades 50-950)
- Typography scale (font sizes, line heights, font weights)
- Spacing scale
- Border radius tokens
- Shadow tokens
- Both light and dark mode variants
Output format: ${format === "tailwind" ? "tailwind.config.js theme extension" : format === "json" ? "JSON design tokens" : "CSS custom properties (:root block)"}
Return ONLY the code, no explanations.`
            },
            { role: "user", content: `Brand colors: ${colors.join(", ")}` }
        ],
        temperature: 0.3,
    });
    const result = response.choices[0].message.content?.trim() || "";
    return result.replace(/^```[\w]*\n?/, "").replace(/\n?```$/, "");
}
