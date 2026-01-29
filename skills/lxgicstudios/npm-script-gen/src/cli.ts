#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-script")
  .description("Generate package.json scripts with AI")
  .version("1.0.0")
  .argument("<tasks>", "Comma-separated list of tasks to generate scripts for")
  .action(async (tasks: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(tasks);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
