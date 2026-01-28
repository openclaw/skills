"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateForm = generateForm;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function generateForm(description, options) {
    const lang = options.typescript ? "TypeScript (TSX)" : "JavaScript (JSX)";
    const lib = options.library || "react-hook-form + zod";
    const res = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You are a senior React developer. Generate a complete form component in ${lang} using ${lib} for validation. Include proper error messages, input types, and accessibility attributes. Return ONLY the code, no explanation.`,
            },
            {
                role: "user",
                content: `Create a form component: ${description}`,
            },
        ],
        temperature: 0.4,
    });
    return res.choices[0].message.content || "";
}
