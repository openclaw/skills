#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { generateLanding } from "./index";

const program = new Command();
program
  .name("ai-landing")
  .description("Generate an HTML landing page from package.json")
  .version("1.0.0")
  .argument("[dir]", "Project directory", ".")
  .option("-o, --output <file>", "Output file", "landing.html")
  .action(async (dir: string, options: { output: string }) => {
    const spinner = ora("Generating landing page...").start();
    try {
      const html = await generateLanding(path.resolve(dir));
      fs.writeFileSync(options.output, html);
      spinner.succeed(`Landing page written to ${options.output}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
