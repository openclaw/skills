#!/usr/bin/env node
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const commander_1 = require("commander");
const ora_1 = __importDefault(require("ora"));
const index_1 = require("./index");
const fs_1 = require("fs");
const program = new commander_1.Command();
program
    .name("ai-comment")
    .description("Add inline comments explaining complex code")
    .version("1.0.0")
    .argument("<file>", "File to comment")
    .option("-s, --style <style>", "Comment style: concise, detailed, beginner", "concise")
    .option("-d, --dry-run", "Print to stdout without modifying file", false)
    .action(async (file, options) => {
    const spinner = (0, ora_1.default)("Analyzing code...").start();
    try {
        const commented = await (0, index_1.addComments)(file, options.style);
        if (options.dryRun) {
            spinner.succeed("Commented code:");
            console.log("\n" + commented);
        }
        else {
            (0, fs_1.writeFileSync)(file, commented);
            spinner.succeed(`Comments added to ${file}`);
        }
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
