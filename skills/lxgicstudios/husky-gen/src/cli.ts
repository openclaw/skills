#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { analyzeProject, generateHooks, installHooks } from "./index";

const program = new Command();
program
  .name("ai-husky")
  .description("Set up git hooks with linting and testing")
  .version("1.0.0")
  .option("-d, --dry-run", "Preview hooks without installing", false)
  .action(async (options: { dryRun: boolean }) => {
    const spinner = ora("Analyzing project...").start();
    try {
      const pkg = await analyzeProject();
      spinner.text = "Generating hooks...";
      const hooks = await generateHooks(pkg);
      if (options.dryRun) {
        spinner.succeed("Generated hooks (dry run):");
        console.log("\n--- pre-commit ---\n" + hooks.preCommit);
        console.log("\n--- pre-push ---\n" + hooks.prePush);
        console.log("\n--- commit-msg ---\n" + hooks.commitMsg);
      } else {
        installHooks(hooks);
        spinner.succeed("Git hooks installed in .husky/");
        console.log("  - pre-commit (lint + typecheck)");
        console.log("  - pre-push (tests)");
        console.log("  - commit-msg (conventional commits)");
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
