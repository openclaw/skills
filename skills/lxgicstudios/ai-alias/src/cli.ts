#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-alias")
  .description("Generate useful shell aliases from your command history")
  .version("1.0.0")
  .action(async () => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(process.cwd());
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
