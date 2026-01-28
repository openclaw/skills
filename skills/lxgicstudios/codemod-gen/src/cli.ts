#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-codemod")
  .description("AI-powered codemod generator for large-scale code changes")
  .version("1.0.0")
  .argument("<description>", "Description of the codemod to generate")
  .action(async (description: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(description);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
