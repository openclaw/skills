#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { generateWorkflow } from "./index";

const program = new Command();

program
  .name("ai-github-action")
  .description("Generate GitHub Actions workflows from plain English")
  .version("1.0.0")
  .argument("<description>", "Describe the workflow you need")
  .option("-o, --output <file>", "Output file path")
  .option("--install", "Write to .github/workflows/ directory", false)
  .action(async (description, opts) => {
    const spinner = ora("Generating workflow...").start();
    try {
      const yaml = await generateWorkflow(description);
      spinner.stop();
      if (opts.install) {
        const dir = ".github/workflows";
        fs.mkdirSync(dir, { recursive: true });
        const file = path.join(dir, "ai-generated.yml");
        fs.writeFileSync(file, yaml);
        console.log(`Workflow written to ${file}`);
      } else if (opts.output) {
        fs.writeFileSync(opts.output, yaml);
        console.log(`Workflow written to ${opts.output}`);
      } else {
        console.log("\n" + yaml + "\n");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
