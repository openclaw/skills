#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { analyzeAndRefactor, applyRefactor, colorDiff } from "./index";

const program = new Command();

program
  .name("ai-refactor")
  .description("Analyze code files and get refactoring suggestions with diffs")
  .version("1.0.0")
  .argument("<file>", "File to analyze")
  .option("--apply", "Apply the refactoring changes to the file")
  .option("--focus <area>", "Focus on a specific area (e.g. 'error handling', 'types')")
  .action(async (file: string, options: { apply?: boolean; focus?: string }) => {
    const spinner = ora("Analyzing your code...").start();

    try {
      const result = await analyzeAndRefactor({
        filePath: file,
        apply: options.apply,
        focus: options.focus,
      });

      spinner.succeed("Analysis complete!");

      console.log("\n" + result.explanation);
      console.log("\n" + colorDiff(result.diff));

      if (options.apply) {
        applyRefactor(file, result.refactored);
        console.log(`\nChanges applied to ${file}`);
      } else {
        console.log("\nRun with --apply to apply these changes.");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
