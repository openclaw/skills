#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-storybook")
  .description("Generate Storybook stories from React components")
  .version("1.0.0")
  .argument("<file>", "Component file to generate stories for")
  .action(async (file: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(file);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
