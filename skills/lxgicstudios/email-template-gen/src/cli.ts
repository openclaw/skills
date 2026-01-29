#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateEmailTemplate } from "./index";

const program = new Command();

program
  .name("ai-email-template")
  .description("Generate responsive email templates from descriptions")
  .version("1.0.0")
  .argument("<description>", "Describe the email template you need")
  .option("-f, --format <format>", "Output format: html, react, or mjml", "html")
  .option("-o, --output <file>", "Write to file")
  .action(async (description, opts) => {
    const spinner = ora("Generating email template...").start();
    try {
      const code = await generateEmailTemplate(description, opts);
      spinner.stop();
      if (opts.output) {
        fs.writeFileSync(opts.output, code);
        console.log(`Template written to ${opts.output}`);
      } else {
        console.log("\n" + code + "\n");
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
