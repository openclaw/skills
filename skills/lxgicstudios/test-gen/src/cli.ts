#!/usr/bin/env node
import { Command } from "commander";
import { generateTests } from "./index";
import * as fs from "fs";

const program = new Command();

program
  .name("ai-test-gen")
  .description("Generate unit tests from source files using AI")
  .version("1.0.0")
  .argument("<files...>", "Source files or glob patterns")
  .option("--framework <name>", "Test framework (jest, vitest, mocha)", "jest")
  .option("-o, --output <file>", "Write output to file")
  .action(async (files: string[], opts) => {
    try {
      const tests = await generateTests({
        files,
        framework: opts.framework,
        output: opts.output,
      });

      if (opts.output) {
        fs.writeFileSync(opts.output, tests);
        console.log(`\nWritten to ${opts.output}`);
      } else {
        console.log("\n" + tests);
      }
    } catch (err: any) {
      console.error("Error:", err.message);
      process.exit(1);
    }
  });

program.parse();
