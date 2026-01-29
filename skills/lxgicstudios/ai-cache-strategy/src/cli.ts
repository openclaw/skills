#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { scanAPIFiles, suggestCacheStrategy } from "./index";

const program = new Command();

program
  .name("ai-cache-strategy")
  .description("Get AI-powered caching strategy suggestions")
  .version("1.0.0")
  .argument("[directory]", "API directory to scan", ".")
  .action(async (directory: string) => {
    const spinner = ora("Scanning API files...").start();
    try {
      const codeChunks = await scanAPIFiles(directory);
      if (codeChunks.length === 0) {
        spinner.warn("No API files found.");
        return;
      }
      spinner.text = `Analyzing ${codeChunks.length} file(s) for caching opportunities...`;
      const analysis = await suggestCacheStrategy(codeChunks);
      spinner.succeed("Caching Strategy Suggestions:");
      console.log(`\n${analysis}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
