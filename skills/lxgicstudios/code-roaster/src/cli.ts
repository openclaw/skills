#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { roastCode } from "./index";

const program = new Command();

program
  .name("ai-roast")
  .description("Get your code roasted with humor and useful feedback")
  .version("1.0.0")
  .argument("<file>", "Code file to roast")
  .option("-i, --intensity <level>", "Roast intensity: mild, medium, savage", "medium")
  .action(async (file: string, options: { intensity: string }) => {
    const spinner = ora("Preparing the roast...").start();
    try {
      const roast = await roastCode(file, options.intensity);
      spinner.succeed("Your roast is served:\n");
      console.log(roast);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
