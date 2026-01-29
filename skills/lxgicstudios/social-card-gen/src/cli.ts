#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateFromFile, Platform } from "./index";

const program = new Command();

program
  .name("ai-social")
  .description("Turn blog posts and READMEs into social media posts")
  .version("1.0.0")
  .argument("<file>", "Path to blog post, README, or text file")
  .option("-p, --platform <platform>", "Target platform (twitter, linkedin, reddit, all)", "all")
  .action(async (file: string, options: { platform: string }) => {
    if (!fs.existsSync(file)) {
      console.error(`File not found: ${file}`);
      process.exit(1);
    }

    const platform = options.platform as Platform;
    const spinner = ora(`Generating ${platform} post(s)...`).start();

    try {
      const results = await generateFromFile(file, platform);
      spinner.succeed("Posts generated!\n");

      for (const [p, post] of Object.entries(results)) {
        const label = p.charAt(0).toUpperCase() + p.slice(1);
        console.log(`--- ${label} ---`);
        console.log(post);
        console.log("");
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
