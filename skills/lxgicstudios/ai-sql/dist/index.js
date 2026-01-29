"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateSQL = generateSQL;
const openai_1 = __importDefault(require("openai"));
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function generateSQL(query, options) {
    const dialect = options.dialect || "PostgreSQL";
    const res = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You are a database expert. Convert natural language to ${dialect} SQL queries. Use best practices: proper indexing hints, parameterized placeholders where appropriate, and clear aliases.${options.schema ? ` The database schema is: ${options.schema}` : ""} Return ONLY the SQL query, no explanation.`,
            },
            {
                role: "user",
                content: query,
            },
        ],
        temperature: 0.2,
    });
    return res.choices[0].message.content || "";
}
