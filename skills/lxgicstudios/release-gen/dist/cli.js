#!/usr/bin/env node
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const commander_1 = require("commander");
const ora_1 = __importDefault(require("ora"));
const index_1 = require("./index");
const program = new commander_1.Command();
program
    .name("ai-release")
    .description("Generate semantic version bump + release notes + tag")
    .version("1.0.0")
    .option("-d, --dry-run", "Preview without creating tag", false)
    .option("--no-tag", "Generate notes without tagging")
    .action(async (options) => {
    const spinner = (0, ora_1.default)("Analyzing commits...").start();
    try {
        const commits = await (0, index_1.getCommitsSinceLastTag)();
        if (!commits.trim())
            throw new Error("No commits found since last tag");
        const currentVersion = await (0, index_1.getCurrentVersion)();
        spinner.text = "Generating release...";
        const release = await (0, index_1.generateRelease)(commits, currentVersion);
        spinner.succeed(`${release.bump} bump: v${currentVersion} → v${release.version}`);
        console.log("\n" + release.notes);
        if (!options.dryRun && options.tag) {
            const tagSpinner = (0, ora_1.default)("Creating tag...").start();
            await (0, index_1.createTag)(release.version, release.notes);
            tagSpinner.succeed(`Tagged v${release.version}`);
        }
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
