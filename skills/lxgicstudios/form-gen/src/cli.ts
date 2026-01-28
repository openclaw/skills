#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateForm } from "./index";

const program = new Command();

program
  .name("ai-form")
  .description("Generate form components with validation from descriptions")
  .version("1.0.0")
  .argument("<description>", "Describe the form you need")
  .option("-t, --typescript", "Generate TypeScript", false)
  .option("-l, --library <lib>", "Validation library", "react-hook-form + zod")
  .option("-o, --output <file>", "Write to file")
  .action(async (description, opts) => {
    const spinner = ora("Generating form...").start();
    try {
      const code = await generateForm(description, opts);
      spinner.stop();
      if (opts.output) {
        fs.writeFileSync(opts.output, code);
        console.log(`Form written to ${opts.output}`);
      } else {
        console.log("\n" + code + "\n");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
