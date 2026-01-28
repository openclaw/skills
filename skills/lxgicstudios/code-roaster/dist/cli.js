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
    .name("ai-roast")
    .description("Get your code roasted with humor and useful feedback")
    .version("1.0.0")
    .argument("<file>", "Code file to roast")
    .option("-i, --intensity <level>", "Roast intensity: mild, medium, savage", "medium")
    .action(async (file, options) => {
    const spinner = (0, ora_1.default)("Preparing the roast...").start();
    try {
        const roast = await (0, index_1.roastCode)(file, options.intensity);
        spinner.succeed("Your roast is served:\n");
        console.log(roast);
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
