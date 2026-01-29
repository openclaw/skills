#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { runLighthouse, summarizeReport, getAIFixes } from "./index";

const program = new Command();

program
  .name("ai-lighthouse")
  .description("Run Lighthouse audit with AI-powered fix suggestions")
  .version("1.0.0")
  .argument("<url>", "URL to audit")
  .action(async (url: string) => {
    const spinner = ora(`Running Lighthouse on ${url}...`).start();
    try {
      const report = runLighthouse(url);
      spinner.text = "Summarizing results...";
      const summary = summarizeReport(report);
      console.log(`\n${summary}\n`);
      spinner.text = "Getting AI fix suggestions...";
      const fixes = await getAIFixes(summary);
      spinner.succeed("AI Fix Suggestions:");
      console.log(`\n${fixes}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
