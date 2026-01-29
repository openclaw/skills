#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { generateSnapshotTest, writeTestFile } from "./index";
import { globSync } from "glob";

const program = new Command();
program
  .name("ai-snapshot-test")
  .description("Generate Jest snapshot tests for React components")
  .version("1.0.0")
  .argument("<file>", "Component file or glob pattern")
  .option("-o, --output <path>", "Custom output path")
  .action(async (file: string, options: { output?: string }) => {
    const files = globSync(file);
    if (files.length === 0) files.push(file);
    for (const f of files) {
      const spinner = ora(`Generating snapshot tests for ${f}...`).start();
      try {
        const result = await generateSnapshotTest(f);
        const outPath = options.output || result.testPath;
        writeTestFile(outPath, result.testCode);
        spinner.succeed(`${outPath}`);
      } catch (err: any) {
        spinner.fail(`Error on ${f}: ${err.message}`);
      }
    }
  });
program.parse();
