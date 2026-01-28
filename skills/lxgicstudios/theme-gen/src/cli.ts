#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { generateTheme } from "./index";

const program = new Command();

program
  .name("ai-theme")
  .description("Generate a design system/theme from brand colors")
  .version("1.0.0")
  .argument("<colors...>", "Brand colors (hex values)")
  .option("-f, --format <type>", "Output format: css, tailwind, json", "css")
  .option("-o, --output <path>", "Output file path")
  .action(async (colors: string[], options: { format: string; output?: string }) => {
    const spinner = ora("Generating design system...").start();
    try {
      const result = await generateTheme(colors, options.format);
      spinner.succeed("Theme generated!");

      if (options.output) {
        fs.writeFileSync(path.resolve(options.output), result, "utf-8");
        console.log(`  Written to ${options.output}`);
      } else {
        console.log("\n" + result);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
