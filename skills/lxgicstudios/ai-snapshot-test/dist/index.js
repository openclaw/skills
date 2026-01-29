"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateSnapshotTest = generateSnapshotTest;
exports.writeTestFile = writeTestFile;
const openai_1 = __importDefault(require("openai"));
const fs_1 = require("fs");
const path_1 = require("path");
const openai = new openai_1.default();
async function generateSnapshotTest(filePath) {
    const code = (0, fs_1.readFileSync)(filePath, "utf-8");
    const ext = filePath.endsWith(".tsx") ? "tsx" : filePath.endsWith(".ts") ? "ts" : filePath.endsWith(".jsx") ? "jsx" : "js";
    const name = (0, path_1.basename)(filePath, `.${ext}`);
    const testPath = (0, path_1.join)((0, path_1.dirname)(filePath), `${name}.snap.test.${ext}`);
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: `You generate Jest snapshot tests for React components. Rules:
- Use @testing-library/react with render
- Test all prop variations and states
- Use toMatchSnapshot() for each render
- Import from the relative source file
- Include tests for: default props, all prop combos, edge cases, conditional renders
Return ONLY the test file code, no explanation.` },
            { role: "user", content: code }
        ],
        temperature: 0.3,
    });
    return { testCode: response.choices[0].message.content?.trim() || "", testPath };
}
function writeTestFile(path, code) {
    (0, fs_1.writeFileSync)(path, code);
}
