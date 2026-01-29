#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import * as path from "path";
import { runDepcheck, checkOutdated, analyzeResults, removeDeps } from "./index";

const program = new Command();

program
  .name("ai-deps")
  .description("Audits your package.json, finds unused deps, flags outdated ones")
  .version("1.0.0")
  .option("-d, --dir <path>", "Project directory", ".")
  .option("-f, --fix", "Auto-remove unused dependencies")
  .action(async (opts) => {
    const spinner = ora("Scanning dependencies...").start();

    try {
      const dir = path.resolve(opts.dir);
      const pkgPath = path.join(dir, "package.json");

      if (!fs.existsSync(pkgPath)) {
        spinner.fail("No package.json found. Are you in a Node.js project?");
        process.exit(1);
      }

      const pkgJson = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));

      spinner.text = "Running depcheck...";
      const depResult = await runDepcheck(dir);

      spinner.text = "Checking for outdated packages...";
      const outdated = await checkOutdated(dir);

      spinner.text = "Analyzing results...";
      const analysis = await analyzeResults(depResult, outdated, pkgJson);

      spinner.stop();

      console.log("\n=== Dependency Audit ===\n");

      if (depResult.unused.length > 0) {
        console.log(`Unused dependencies: ${depResult.unused.join(", ")}`);
      }
      if (depResult.unusedDev.length > 0) {
        console.log(`Unused devDependencies: ${depResult.unusedDev.join(", ")}`);
      }
      if (outdated.length > 0) {
        console.log(`Outdated packages: ${outdated.join(", ")}`);
      }
      if (Object.keys(depResult.missing).length > 0) {
        console.log(`Missing dependencies: ${Object.keys(depResult.missing).join(", ")}`);
      }

      console.log(`\n=== Analysis ===\n\n${analysis}\n`);

      if (opts.fix && depResult.unused.length > 0) {
        const fixSpinner = ora("Removing unused dependencies...").start();
        await removeDeps(dir, depResult.unused);
        fixSpinner.succeed(`Removed: ${depResult.unused.join(", ")}`);
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
