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
    .name("ai-audit-fix")
    .description("Analyze npm audit output with AI and get actionable fix suggestions")
    .version("1.0.0")
    .option("-d, --dir <path>", "Project directory to audit", ".")
    .action(async (opts) => {
    const spinner = (0, ora_1.default)("Running npm audit...").start();
    try {
        const auditOutput = await (0, index_1.getAuditOutput)();
        spinner.text = "Analyzing vulnerabilities with AI...";
        const analysis = await (0, index_1.analyzeAudit)(auditOutput);
        spinner.stop();
        console.log("\n" + analysis + "\n");
    }
    catch (err) {
        spinner.fail(err.message);
        process.exit(1);
    }
});
program.parse();
