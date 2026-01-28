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
const index_1 = require("./index");
const program = new commander_1.Command();
program
    .name("ai-form")
    .description("Generate form components with validation from descriptions")
    .version("1.0.0")
    .argument("<description>", "Describe the form you need")
    .option("-t, --typescript", "Generate TypeScript", false)
    .option("-l, --library <lib>", "Validation library", "react-hook-form + zod")
    .option("-o, --output <file>", "Write to file")
    .action(async (description, opts) => {
    const spinner = (0, ora_1.default)("Generating form...").start();
    try {
        const code = await (0, index_1.generateForm)(description, opts);
        spinner.stop();
        if (opts.output) {
            fs.writeFileSync(opts.output, code);
            console.log(`Form written to ${opts.output}`);
        }
        else {
            console.log("\n" + code + "\n");
        }
    }
    catch (err) {
        spinner.fail(err.message);
        process.exit(1);
    }
});
program.parse();
