#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const commander_1 = require("commander");
const ora_1 = __importDefault(require("ora"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const index_1 = require("./index");
const program = new commander_1.Command();
program
    .name("ai-github-action")
    .description("Generate GitHub Actions workflows from plain English")
    .version("1.0.0")
    .argument("<description>", "Describe the workflow you need")
    .option("-o, --output <file>", "Output file path")
    .option("--install", "Write to .github/workflows/ directory", false)
    .action(async (description, opts) => {
    const spinner = (0, ora_1.default)("Generating workflow...").start();
    try {
        const yaml = await (0, index_1.generateWorkflow)(description);
        spinner.stop();
        if (opts.install) {
            const dir = ".github/workflows";
            fs.mkdirSync(dir, { recursive: true });
            const file = path.join(dir, "ai-generated.yml");
            fs.writeFileSync(file, yaml);
            console.log(`Workflow written to ${file}`);
        }
        else if (opts.output) {
            fs.writeFileSync(opts.output, yaml);
            console.log(`Workflow written to ${opts.output}`);
        }
        else {
            console.log("\n" + yaml + "\n");
        }
    }
    catch (err) {
        spinner.fail(err.message);
        process.exit(1);
    }
});
program.parse();
