#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { generateSeedData } from "./index";

const program = new Command();

program
  .name("ai-seed")
  .description("Generate realistic database seed data from your schema")
  .version("1.0.0")
  .argument("<schema>", "Path to schema file (Prisma, SQL, etc.)")
  .option("-n, --count <number>", "Records per table", "10")
  .option("-o, --output <path>", "Output file path")
  .action(async (schema: string, options: { count: string; output?: string }) => {
    const spinner = ora("Generating seed data...").start();
    try {
      const result = await generateSeedData(schema, parseInt(options.count));
      spinner.succeed("Seed data generated!");

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
