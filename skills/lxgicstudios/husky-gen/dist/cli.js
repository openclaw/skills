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
    .name("ai-husky")
    .description("Set up git hooks with linting and testing")
    .version("1.0.0")
    .option("-d, --dry-run", "Preview hooks without installing", false)
    .action(async (options) => {
    const spinner = (0, ora_1.default)("Analyzing project...").start();
    try {
        const pkg = await (0, index_1.analyzeProject)();
        spinner.text = "Generating hooks...";
        const hooks = await (0, index_1.generateHooks)(pkg);
        if (options.dryRun) {
            spinner.succeed("Generated hooks (dry run):");
            console.log("\n--- pre-commit ---\n" + hooks.preCommit);
            console.log("\n--- pre-push ---\n" + hooks.prePush);
            console.log("\n--- commit-msg ---\n" + hooks.commitMsg);
        }
        else {
            (0, index_1.installHooks)(hooks);
            spinner.succeed("Git hooks installed in .husky/");
            console.log("  - pre-commit (lint + typecheck)");
            console.log("  - pre-push (tests)");
            console.log("  - commit-msg (conventional commits)");
        }
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
