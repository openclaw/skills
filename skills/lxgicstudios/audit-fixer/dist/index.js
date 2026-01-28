"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAuditOutput = getAuditOutput;
exports.analyzeAudit = analyzeAudit;
const openai_1 = __importDefault(require("openai"));
const child_process_1 = require("child_process");
const openai = new openai_1.default({ apiKey: process.env.OPENAI_API_KEY });
async function getAuditOutput() {
    try {
        return (0, child_process_1.execSync)("npm audit --json 2>/dev/null", { encoding: "utf-8" });
    }
    catch (err) {
        return err.stdout || err.message;
    }
}
async function analyzeAudit(auditJson) {
    const res = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: "You are a security expert. Analyze npm audit JSON output and provide: 1) A summary of vulnerabilities found (critical, high, moderate, low counts), 2) For each vulnerability, explain what it is and the risk, 3) Specific fix commands (npm audit fix, manual overrides, or package replacements). Be concise and actionable.",
            },
            {
                role: "user",
                content: `Analyze this npm audit output and suggest fixes:\n\n${auditJson.slice(0, 8000)}`,
            },
        ],
        temperature: 0.3,
    });
    return res.choices[0].message.content || "No analysis generated.";
}
