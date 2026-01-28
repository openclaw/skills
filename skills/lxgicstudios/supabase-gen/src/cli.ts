#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { generate } from "./index";

const program = new Command();
program
  .name("ai-supabase-gen")
  .description("Generate Supabase RLS policies from a Prisma schema file")
  .version("1.0.0")
  .argument("<file>", "Path to Prisma schema file")
  .action(async (input: string) => {
    const spinner = ora("Generating...").start();
    try {
      const result = await generate(input);
      spinner.succeed("Done:\n");
      console.log(result);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
