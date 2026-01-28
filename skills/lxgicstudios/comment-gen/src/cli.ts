#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { addComments } from "./index";
import { writeFileSync } from "fs";

const program = new Command();
program
  .name("ai-comment")
  .description("Add inline comments explaining complex code")
  .version("1.0.0")
  .argument("<file>", "File to comment")
  .option("-s, --style <style>", "Comment style: concise, detailed, beginner", "concise")
  .option("-d, --dry-run", "Print to stdout without modifying file", false)
  .action(async (file: string, options: { style: string; dryRun: boolean }) => {
    const spinner = ora("Analyzing code...").start();
    try {
      const commented = await addComments(file, options.style);
      if (options.dryRun) {
        spinner.succeed("Commented code:");
        console.log("\n" + commented);
      } else {
        writeFileSync(file, commented);
        spinner.succeed(`Comments added to ${file}`);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
