#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { collectRouteFiles, generateApiDocs, writeDocs } from "./index";

const program = new Command();
program
  .name("ai-api-docs")
  .description("Generate API documentation from route files")
  .version("1.0.0")
  .argument("<dir>", "Directory containing route files")
  .option("-f, --format <type>", "Output format: markdown or openapi", "markdown")
  .option("-o, --output <path>", "Output file path", "API_DOCS.md")
  .action(async (dir: string, options: { format: string; output: string }) => {
    const spinner = ora("Scanning route files...").start();
    try {
      const files = collectRouteFiles(dir);
      if (files.length === 0) throw new Error("No route files found");
      spinner.text = `Generating docs from ${files.length} files...`;
      const docs = await generateApiDocs(files, options.format);
      const outPath = options.format === "openapi" ? options.output.replace(".md", ".yaml") : options.output;
      writeDocs(outPath, docs);
      spinner.succeed(`API docs written to ${outPath} (${files.length} files analyzed)`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
