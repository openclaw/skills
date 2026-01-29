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
    .name("ai-sql")
    .description("Convert natural language to SQL queries")
    .version("1.0.0")
    .argument("<query>", "Describe what you want to query")
    .option("-d, --dialect <dialect>", "SQL dialect", "PostgreSQL")
    .option("-s, --schema <schema>", "Table schema context")
    .action(async (query, opts) => {
    const spinner = (0, ora_1.default)("Generating SQL...").start();
    try {
        const sql = await (0, index_1.generateSQL)(query, opts);
        spinner.stop();
        console.log("\n" + sql + "\n");
    }
    catch (err) {
        spinner.fail(err.message);
        process.exit(1);
    }
});
program.parse();
