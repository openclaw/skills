"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.collectRouteFiles = collectRouteFiles;
exports.generateApiDocs = generateApiDocs;
exports.writeDocs = writeDocs;
const openai_1 = __importDefault(require("openai"));
const fs_1 = require("fs");
const path_1 = require("path");
const openai = new openai_1.default();
function collectRouteFiles(dir) {
    const files = [];
    const entries = (0, fs_1.readdirSync)(dir);
    for (const entry of entries) {
        const full = (0, path_1.join)(dir, entry);
        if ((0, fs_1.statSync)(full).isDirectory()) {
            files.push(...collectRouteFiles(full));
        }
        else if ([".ts", ".js", ".tsx", ".jsx"].includes((0, path_1.extname)(full))) {
            files.push(full);
        }
    }
    return files;
}
async function generateApiDocs(files, format) {
    const code = files.map(f => `// ${f}\n${(0, fs_1.readFileSync)(f, "utf-8")}`).join("\n\n");
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: `You generate API documentation from route/endpoint code. Output format: ${format}.
For markdown: include method, path, description, request/response examples, parameters, error codes.
For openapi: return valid OpenAPI 3.0 YAML spec.
Be thorough and accurate based on the actual code.` },
            { role: "user", content: code.slice(0, 12000) }
        ],
        temperature: 0.3,
    });
    return response.choices[0].message.content?.trim() || "";
}
function writeDocs(path, content) {
    (0, fs_1.writeFileSync)(path, content);
}
