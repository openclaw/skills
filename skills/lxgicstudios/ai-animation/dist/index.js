"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateAnimation = generateAnimation;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function generateAnimation(description, options) {
    const format = options.format || "both";
    let outputInstructions = "";
    if (format === "css")
        outputInstructions = "Generate CSS @keyframes animation only.";
    else if (format === "framer")
        outputInstructions = "Generate Framer Motion animation config only (motion component props).";
    else
        outputInstructions = "Generate both CSS @keyframes and Framer Motion equivalent.";
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
