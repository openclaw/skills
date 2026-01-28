#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-data-transform")
  .description("Generate ETL and data transformation scripts with AI")
  .version("1.0.0")
  .argument("<transformation>", "Description of the data transformation")
  .action(async (transformation: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(transformation);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
