#!/usr/bin/env node
import { Command } from "commander";
import ora from "ora";
import { getCommitsSinceLastTag, getCurrentVersion, generateRelease, createTag } from "./index";

const program = new Command();
program
  .name("ai-release")
  .description("Generate semantic version bump + release notes + tag")
  .version("1.0.0")
  .option("-d, --dry-run", "Preview without creating tag", false)
  .option("--no-tag", "Generate notes without tagging")
  .action(async (options: { dryRun: boolean; tag: boolean }) => {
    const spinner = ora("Analyzing commits...").start();
    try {
      const commits = await getCommitsSinceLastTag();
      if (!commits.trim()) throw new Error("No commits found since last tag");
      const currentVersion = await getCurrentVersion();
      spinner.text = "Generating release...";
      const release = await generateRelease(commits, currentVersion);
      spinner.succeed(`${release.bump} bump: v${currentVersion} → v${release.version}`);
      console.log("\n" + release.notes);
      if (!options.dryRun && options.tag) {
        const tagSpinner = ora("Creating tag...").start();
        await createTag(release.version, release.notes);
        tagSpinner.succeed(`Tagged v${release.version}`);
      }
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });
program.parse();
