#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { createBranch } from "./index";

const program = new Command();

program
  .name("ai-branch")
  .description("Generate descriptive git branch names from plain English")
  .version("1.0.0")
  .argument("<description>", "What you're working on")
  .option("-c, --checkout", "Create and checkout the branch", false)
  .action(async (description: string, options: { checkout: boolean }) => {
    const spinner = ora("Generating branch name...").start();
    try {
      const branchName = await createBranch(description, options.checkout);
      spinner.succeed(`Branch: ${branchName}`);
      if (options.checkout) {
        console.log(`  Switched to new branch '${branchName}'`);
      } else {
        console.log(`  Run: git checkout -b ${branchName}`);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
