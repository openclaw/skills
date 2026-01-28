"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getCommitsSinceLastTag = getCommitsSinceLastTag;
exports.getCurrentVersion = getCurrentVersion;
exports.generateRelease = generateRelease;
exports.createTag = createTag;
const openai_1 = __importDefault(require("openai"));
const simple_git_1 = __importDefault(require("simple-git"));
const fs_1 = require("fs");
const path_1 = require("path");
const openai = new openai_1.default();
const git = (0, simple_git_1.default)();
async function getCommitsSinceLastTag() {
    try {
        const tags = await git.tags();
        const latest = tags.latest;
        if (latest) {
            const log = await git.log({ from: latest, to: "HEAD" });
            return log.all.map(c => c.message).join("\n");
        }
    }
    catch { }
    const log = await git.log({ maxCount: 20 });
    return log.all.map(c => c.message).join("\n");
}
async function getCurrentVersion() {
    try {
        const pkg = JSON.parse((0, fs_1.readFileSync)((0, path_1.join)(process.cwd(), "package.json"), "utf-8"));
        return pkg.version || "0.0.0";
    }
    catch {
        return "0.0.0";
    }
}
async function generateRelease(commits, currentVersion) {
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: `You analyze git commits and determine the semantic version bump. Current version: ${currentVersion}.
Return JSON with: { "bump": "patch|minor|major", "version": "x.y.z", "notes": "markdown release notes" }
Follow semver: breaking changes = major, new features = minor, fixes = patch.
Return ONLY valid JSON.` },
            { role: "user", content: commits }
        ],
        temperature: 0.3,
    });
    return JSON.parse(response.choices[0].message.content || "{}");
}
async function createTag(version, notes) {
    await git.addAnnotatedTag(`v${version}`, notes);
}
