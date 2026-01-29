#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { resolveFile, resolveConflicts } from "./index";

const program = new Command();

program
  .name("ai-merge-resolve")
  .description("Resolve git merge conflicts intelligently using AI")
  .version("1.0.0")
  .argument("[file]", "File with merge conflicts")
  .option("-w, --write", "Write resolved content back to file", false)
  .action(async (file: string | undefined, options: { write: boolean }) => {
    const spinner = ora("Resolving merge conflicts...").start();
    try {
      let resolved: string;
      if (file) {
        resolved = await resolveFile(file);
      } else {
        const chunks: Buffer[] = [];
        for await (const chunk of process.stdin) chunks.push(chunk);
        const content = Buffer.concat(chunks).toString("utf-8");
        resolved = await resolveConflicts(content);
      }
      spinner.succeed("Conflicts resolved!");
      if (options.write && file) {
        fs.writeFileSync(file, resolved);
        console.log(`  Written to ${file}`);
      } else {
        console.log(resolved);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
