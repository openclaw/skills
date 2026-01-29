#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { scanSourceFiles, fixCoreVitals } from "./index";

const program = new Command();

program
  .name("ai-core-vitals")
  .description("Fix Core Web Vitals issues with AI guidance")
  .version("1.0.0")
  .argument("[directory]", "Source directory to scan", ".")
  .action(async (directory: string) => {
    const spinner = ora("Scanning for Core Web Vitals issues...").start();
    try {
      const codeChunks = await scanSourceFiles(directory);
      if (codeChunks.length === 0) {
        spinner.warn("No source files found.");
        return;
      }
      spinner.text = `Analyzing ${codeChunks.length} file(s) for CWV issues...`;
      const analysis = await fixCoreVitals(codeChunks);
      spinner.succeed("Core Web Vitals Analysis:");
      console.log(`\n${analysis}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
