#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateTailwind } from "./index";

const program = new Command();
program
  .name("ai-tailwind")
  .description("Generate tailwind.config from design system colors")
  .version("1.0.0")
  .argument("<colors...>", "Brand colors (hex values)")
  .option("-o, --output <file>", "Output file", "tailwind.config.js")
  .action(async (colors: string[], options: { output: string }) => {
    const spinner = ora("Generating Tailwind config...").start();
    try {
      const config = await generateTailwind(colors);
      fs.writeFileSync(options.output, config);
      spinner.succeed(`Tailwind config written to ${options.output}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
