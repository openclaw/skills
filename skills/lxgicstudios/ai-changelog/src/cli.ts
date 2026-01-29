#!/usr/bin/env node
import { Command } from "commander";
import { generateChangelog } from "./index";
import * as fs from "fs";

const program = new Command();

program
  .name("ai-changelog")
  .description("Generate a clean changelog from git history using AI")
  .version("1.0.0")
  .requiredOption("--from <ref>", "Start tag, branch, or commit")
  .requiredOption("--to <ref>", "End tag, branch, or commit (default: HEAD)", "HEAD")
  .option("-o, --output <file>", "Write output to file instead of stdout")
  .action(async (opts) => {
    try {
      const changelog = await generateChangelog({
        from: opts.from,
        to: opts.to,
        output: opts.output,
      });

      if (opts.output) {
        fs.writeFileSync(opts.output, changelog);
        console.log(`\nWritten to ${opts.output}`);
      } else {
        console.log("\n" + changelog);
      }
    } catch (err: any) {
      console.error("Error:", err.message);
      process.exit(1);
    }
  });

program.parse();
