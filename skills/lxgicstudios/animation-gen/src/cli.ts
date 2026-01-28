#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateAnimation } from "./index";

const program = new Command();

program
  .name("ai-animation")
  .description("Generate CSS and Framer Motion animations from descriptions")
  .version("1.0.0")
  .argument("<description>", "Describe the animation you want")
  .option("-f, --format <format>", "Output format: css, framer, or both", "both")
  .option("-o, --output <file>", "Write to file")
  .action(async (description, opts) => {
    const spinner = ora("Generating animation...").start();
    try {
      const code = await generateAnimation(description, opts);
      spinner.stop();
      if (opts.output) {
        fs.writeFileSync(opts.output, code);
        console.log(`Animation written to ${opts.output}`);
      } else {
        console.log("\n" + code + "\n");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
