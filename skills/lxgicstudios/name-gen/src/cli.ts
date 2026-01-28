#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { stashWithName, getStashDiff, generateStashName } from "./index";

const program = new Command();
program
  .name("ai-stash-name")
  .description("Name your git stashes meaningfully using AI")
  .version("1.0.0")
  .option("-d, --dry-run", "Show the name without stashing", false)
  .action(async (options: { dryRun: boolean }) => {
    const spinner = ora("Analyzing changes...").start();
    try {
      if (options.dryRun) {
        const diff = await getStashDiff();
        const name = await generateStashName(diff);
        spinner.succeed(`Suggested name: ${name}`);
      } else {
        const name = await stashWithName();
        spinner.succeed(`Stashed as: ${name}`);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
