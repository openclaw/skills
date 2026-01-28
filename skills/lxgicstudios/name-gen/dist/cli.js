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
    .name("ai-stash-name")
    .description("Name your git stashes meaningfully using AI")
    .version("1.0.0")
    .option("-d, --dry-run", "Show the name without stashing", false)
    .action(async (options) => {
    const spinner = (0, ora_1.default)("Analyzing changes...").start();
    try {
        if (options.dryRun) {
            const diff = await (0, index_1.getStashDiff)();
            const name = await (0, index_1.generateStashName)(diff);
            spinner.succeed(`Suggested name: ${name}`);
        }
        else {
            const name = await (0, index_1.stashWithName)();
            spinner.succeed(`Stashed as: ${name}`);
        }
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
