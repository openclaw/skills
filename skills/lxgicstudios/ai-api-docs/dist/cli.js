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
    .name("ai-api-docs")
    .description("Generate API documentation from route files")
    .version("1.0.0")
    .argument("<dir>", "Directory containing route files")
    .option("-f, --format <type>", "Output format: markdown or openapi", "markdown")
    .option("-o, --output <path>", "Output file path", "API_DOCS.md")
    .action(async (dir, options) => {
    const spinner = (0, ora_1.default)("Scanning route files...").start();
    try {
        const files = (0, index_1.collectRouteFiles)(dir);
        if (files.length === 0)
            throw new Error("No route files found");
        spinner.text = `Generating docs from ${files.length} files...`;
        const docs = await (0, index_1.generateApiDocs)(files, options.format);
        const outPath = options.format === "openapi" ? options.output.replace(".md", ".yaml") : options.output;
        (0, index_1.writeDocs)(outPath, docs);
        spinner.succeed(`API docs written to ${outPath} (${files.length} files analyzed)`);
    }
    catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
    }
});
program.parse();
