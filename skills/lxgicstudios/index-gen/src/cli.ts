#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { suggestIndexes } from "./index";

const program = new Command();

program
  .name("ai-index")
  .description("Suggest database indexes from query patterns")
  .version("1.0.0")
  .argument("<path>", "Directory or file with query patterns")
  .option("-o, --output <path>", "Output file path")
  .action(async (queryPath: string, options: { output?: string }) => {
    const spinner = ora("Analyzing query patterns...").start();
    try {
      const result = await suggestIndexes(queryPath);
      spinner.succeed("Index suggestions ready!");

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
