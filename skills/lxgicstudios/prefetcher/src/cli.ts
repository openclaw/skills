#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { scanPages, suggestPrefetch } from "./index";

const program = new Command();

program
  .name("ai-prefetch")
  .description("AI suggests routes and data to prefetch")
  .version("1.0.0")
  .argument("[directory]", "Pages directory to scan", ".")
  .action(async (directory: string) => {
    const spinner = ora("Scanning pages...").start();
    try {
      const codeChunks = await scanPages(directory);
      if (codeChunks.length === 0) {
        spinner.warn("No page files found.");
        return;
      }
      spinner.text = `Analyzing ${codeChunks.length} page(s) for prefetch opportunities...`;
      const analysis = await suggestPrefetch(codeChunks);
      spinner.succeed("Prefetch Suggestions:");
      console.log(`\n${analysis}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
