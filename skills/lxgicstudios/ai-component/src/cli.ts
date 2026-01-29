#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateComponent } from "./index";

const program = new Command();

program
  .name("ai-component")
  .description("Generate React components from plain English descriptions")
  .version("1.0.0")
  .argument("<description>", "Describe the component you want")
  .option("-t, --typescript", "Generate TypeScript (TSX)", false)
  .option("--tailwind", "Use Tailwind CSS", false)
  .option("-o, --output <file>", "Write to file instead of stdout")
  .action(async (description, opts) => {
    const spinner = ora("Generating component...").start();
    try {
      const code = await generateComponent(description, opts);
      spinner.stop();
      if (opts.output) {
        fs.writeFileSync(opts.output, code);
        console.log(`Component written to ${opts.output}`);
      } else {
        console.log("\n" + code + "\n");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
