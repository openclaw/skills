#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { convertCssToTailwind } from "./index";

const program = new Command();

program
  .name("ai-css-to-tailwind")
  .description("Convert CSS files to Tailwind utility classes")
  .version("1.0.0")
  .argument("<file>", "CSS file to convert")
  .option("-o, --output <path>", "Output file path")
  .action(async (file: string, options: { output?: string }) => {
    const spinner = ora("Converting CSS to Tailwind...").start();
    try {
      const result = await convertCssToTailwind(file);
      spinner.succeed("Conversion complete!");

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
