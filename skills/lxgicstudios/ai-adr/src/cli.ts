#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();

program
  .name("ai-adr")
  .description("Generate Architecture Decision Records with AI")
  .version("1.0.0")
  .argument("<decision>", "The architectural decision to document")
  .action(async (decision: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(decision);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
