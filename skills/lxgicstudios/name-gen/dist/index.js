"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getStashDiff = getStashDiff;
exports.generateStashName = generateStashName;
exports.stashWithName = stashWithName;
const openai_1 = __importDefault(require("openai"));
const simple_git_1 = __importDefault(require("simple-git"));
const openai = new openai_1.default();
const git = (0, simple_git_1.default)();
async function getStashDiff() {
    const diff = await git.diff(["--cached"]);
    const unstaged = await git.diff();
    return (diff + "\n" + unstaged).slice(0, 4000);
}
async function generateStashName(diff) {
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: "You generate short, descriptive git stash names from diffs. Return ONLY the stash message, no quotes. Keep it under 60 chars. Be specific about what changed." },
            { role: "user", content: diff }
        ],
        temperature: 0.3,
    });
    return response.choices[0].message.content?.trim() || "wip: misc changes";
}
async function stashWithName() {
    const diff = await getStashDiff();
    if (!diff.trim())
        throw new Error("No changes to stash");
    const name = await generateStashName(diff);
    await git.stash(["push", "-m", name]);
    return name;
}
