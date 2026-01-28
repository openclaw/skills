#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import { scanImages, getOptimizationAdvice } from "./index";

const program = new Command();

program
  .name("ai-image-optimize")
  .description("AI-powered image optimization suggestions")
  .version("1.0.0")
  .argument("[directory]", "Images directory to scan", ".")
  .action(async (directory: string) => {
    const spinner = ora("Scanning images...").start();
    try {
      const images = await scanImages(directory);
      if (images.length === 0) {
        spinner.warn("No images found.");
        return;
      }
      spinner.text = `Analyzing ${images.length} image(s)...`;
      const advice = await getOptimizationAdvice(images);
      spinner.succeed(`Image Optimization Report (${images.length} images):`);
      console.log(`\n${advice}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
