#!/usr/bin/env node
import { Command } from "commander";
import { reviewStagedChanges } from "./index";

const program = new Command();

program
  .name("ai-code-review")
  .description("Get AI code review on your staged git changes")
  .version("1.0.0")
  .action(async () => {
    try {
      await reviewStagedChanges();
    } catch (err: any) {
      console.error("Error:", err.message);
      process.exit(1);
    }
  });

program.parse();
