#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { scanProject, generateWorkflow } from "./index";

const program = new Command();

program
  .name("ai-ci")
  .description("Generates CI/CD workflows from project analysis")
  .version("1.0.0")
  .option("-p, --preview", "Preview without writing")
  .option("--provider <provider>", "CI provider", "github")
  .option("--deploy <target>", "Deploy target (vercel, netlify, aws, docker)")
  .option("-d, --dir <path>", "Project directory", ".")
  .option("-o, --output <path>", "Output path")
  .action(async (opts) => {
    const spinner = ora("Scanning project...").start();

    try {
      const dir = path.resolve(opts.dir);
      const info = await scanProject(dir);

      if (info.files.length === 0) {
        spinner.warn("No project files found. Are you in the right directory?");
        process.exit(1);
      }

      spinner.text = `Found ${info.files.length} config files. Generating workflow...`;

      const workflow = await generateWorkflow(info, opts.provider, opts.deploy);

      const defaultOutput = opts.provider === "github"
        ? ".github/workflows/ci.yml"
        : "ci-workflow.yml";
      const outPath = path.resolve(opts.output || defaultOutput);

      if (opts.preview) {
        spinner.stop();
        console.log(`\n--- Generated ${opts.provider} workflow ---\n`);
        console.log(workflow);
        console.log("\n-----------------------------------------\n");
      } else {
        const outDir = path.dirname(outPath);
        if (!fs.existsSync(outDir)) {
          fs.mkdirSync(outDir, { recursive: true });
        }
        fs.writeFileSync(outPath, workflow + "\n");
        spinner.succeed(`Workflow written to ${outPath}`);
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
