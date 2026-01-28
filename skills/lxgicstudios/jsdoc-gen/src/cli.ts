#!/usr/bin/env node
import { Command } from "commander";
import { addDocs } from "./index";

const program = new Command();

program
  .name("ai-docs")
  .description("Add JSDoc/TSDoc comments to your source files using AI")
  .version("1.0.0")
  .argument("<paths...>", "Files, directories, or glob patterns")
  .option("--style <style>", "Doc style: jsdoc or tsdoc", "jsdoc")
  .option("-w, --write", "Write changes back to files (default: stdout only)", false)
  .action(async (paths: string[], opts) => {
    try {
      await addDocs({
        paths,
        style: opts.style,
        write: opts.write,
      });
    } catch (err: any) {
      console.error("Error:", err.message);
      process.exit(1);
    }
  });

program.parse();
