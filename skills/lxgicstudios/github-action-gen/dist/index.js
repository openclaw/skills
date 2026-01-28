"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateWorkflow = generateWorkflow;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function generateWorkflow(description) {
    const res = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: "You are a DevOps expert. Generate a complete GitHub Actions workflow YAML file based on the description. Use best practices: proper triggers, caching, environment variables, and job dependencies. Return ONLY the YAML content, no explanation.",
            },
            {
                role: "user",
                content: `Create a GitHub Actions workflow: ${description}`,
            },
        ],
        temperature: 0.3,
    });
    return res.choices[0].message.content || "";
}
