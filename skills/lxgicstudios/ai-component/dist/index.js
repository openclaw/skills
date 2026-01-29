"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateComponent = generateComponent;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function generateComponent(description, options) {
    const lang = options.typescript ? "TypeScript (TSX)" : "JavaScript (JSX)";
    const styling = options.tailwind ? "Tailwind CSS classes" : "CSS modules or inline styles";
    const res = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You are a senior React developer. Generate a complete, production-ready React component in ${lang} using ${styling}. Include proper props typing, sensible defaults, and clean structure. Return ONLY the code, no explanation.`,
            },
            {
                role: "user",
                content: `Create a React component: ${description}`,
            },
        ],
        temperature: 0.4,
    });
    return res.choices[0].message.content || "";
}
