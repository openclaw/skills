#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generateSQL } from "./index";

const program = new Command();

program
  .name("ai-sql")
  .description("Convert natural language to SQL queries")
  .version("1.0.0")
  .argument("<query>", "Describe what you want to query")
  .option("-d, --dialect <dialect>", "SQL dialect", "PostgreSQL")
  .option("-s, --schema <schema>", "Table schema context")
  .action(async (query, opts) => {
    const spinner = ora("Generating SQL...").start();
    try {
      const sql = await generateSQL(query, opts);
      spinner.stop();
      console.log("\n" + sql + "\n");
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
