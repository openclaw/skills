#!/usr/bin/env node
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const commander_1 = require("commander");
const ora_1 = __importDefault(require("ora"));
const index_1 = require("./index");
const glob_1 = require("glob");
const program = new commander_1.Command();
program
    .name("ai-snapshot-test")
    .description("Generate Jest snapshot tests for React components")
    .version("1.0.0")
    .argument("<file>", "Component file or glob pattern")
    .option("-o, --output <path>", "Custom output path")
    .action(async (file, options) => {
    const files = (0, glob_1.globSync)(file);
    if (files.length === 0)
        files.push(file);
    for (const f of files) {
        const spinner = (0, ora_1.default)(`Generating snapshot tests for ${f}...`).start();
        try {
            const result = await (0, index_1.generateSnapshotTest)(f);
            const outPath = options.output || result.testPath;
            (0, index_1.writeTestFile)(outPath, result.testCode);
            spinner.succeed(`${outPath}`);
        }
        catch (err) {
            spinner.fail(`Error on ${f}: ${err.message}`);
        }
    }
});
program.parse();
