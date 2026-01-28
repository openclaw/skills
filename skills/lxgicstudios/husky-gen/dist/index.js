"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyzeProject = analyzeProject;
exports.generateHooks = generateHooks;
exports.installHooks = installHooks;
const openai_1 = __importDefault(require("openai"));
const fs_1 = require("fs");
const path_1 = require("path");
const child_process_1 = require("child_process");
const openai = new openai_1.default();
async function analyzeProject() {
    const cwd = process.cwd();
    let pkgContent = "{}";
    try {
        pkgContent = (0, fs_1.readFileSync)((0, path_1.join)(cwd, "package.json"), "utf-8");
    }
    catch { }
    return pkgContent;
}
async function generateHooks(pkgContent) {
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: `You generate git hook scripts based on a project's package.json. Return JSON:
{ "preCommit": "#!/bin/sh\\nscript...", "prePush": "#!/bin/sh\\nscript...", "commitMsg": "#!/bin/sh\\nscript..." }
Pre-commit: lint staged files, type-check if typescript.
Pre-push: run tests.
Commit-msg: validate conventional commit format.
Use the project's actual scripts (lint, test, typecheck) from package.json.
Return ONLY valid JSON.` },
            { role: "user", content: pkgContent }
        ],
        temperature: 0.3,
    });
    return JSON.parse(response.choices[0].message.content || "{}");
}
function installHooks(hooks) {
    const hooksDir = (0, path_1.join)(process.cwd(), ".husky");
    (0, fs_1.mkdirSync)(hooksDir, { recursive: true });
    const write = (name, content) => {
        const path = (0, path_1.join)(hooksDir, name);
        (0, fs_1.writeFileSync)(path, content);
        (0, fs_1.chmodSync)(path, "755");
    };
    write("pre-commit", hooks.preCommit);
    write("pre-push", hooks.prePush);
    write("commit-msg", hooks.commitMsg);
    try {
        (0, child_process_1.execSync)("git config core.hooksPath .husky", { stdio: "pipe" });
    }
    catch { }
}
