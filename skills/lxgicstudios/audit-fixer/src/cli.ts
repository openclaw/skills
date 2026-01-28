#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { getAuditOutput, analyzeAudit } from "./index";

const program = new Command();

program
  .name("ai-audit-fix")
  .description("Analyze npm audit output with AI and get actionable fix suggestions")
  .version("1.0.0")
  .option("-d, --dir <path>", "Project directory to audit", ".")
  .action(async (opts) => {
    const spinner = ora("Running npm audit...").start();

    try {
      const auditOutput = await getAuditOutput();
      spinner.text = "Analyzing vulnerabilities with AI...";
      const analysis = await analyzeAudit(auditOutput);
      spinner.stop();
      console.log("\n" + analysis + "\n");
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
