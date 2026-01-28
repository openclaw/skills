#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-cover-letter")
  .description("Generate tailored cover letters with AI")
  .version("1.0.0")
  .argument("<role>", "Job role and company description")
  .action(async (role: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(role);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
